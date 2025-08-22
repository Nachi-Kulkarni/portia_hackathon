# Apply compatibility fix for Python < 3.12 BEFORE importing anything that uses Portia
try:
    import src.compatibility_fix  # This patches typing.override
except ImportError:
    pass  # Continue without compatibility fix

from portia.execution_hooks import ExecutionHooks
from portia.clarification import ActionClarification, UserVerificationClarification
from src.agents.escalation_manager import EscalationManager, EscalationContext
from src.hooks.audit_logger import AuditLoggerTool
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InsuranceExecutionHooks:
    """Custom execution hooks for insurance claim processing"""
    
    def __init__(self):
        self.escalation_manager = EscalationManager()
        self.audit_logger = AuditLoggerTool()
    
    def before_tool_call(self, ctx, tool, *args, **kwargs) -> Any:
        """Intercept tool calls for compliance and escalation checks with proper context"""
        try:
            # Log the tool call attempt with proper context
            audit_result = self.audit_logger.run(
                ctx=ctx,  # Pass the real context with plan_run_id, user_id
                action_type="tool_call_attempt",
                tool_name=getattr(tool, 'name', type(tool).__name__),
                arguments={"args": args, "kwargs": kwargs},
                timestamp=datetime.now(),
                justification=f"Pre-execution audit for {getattr(tool, 'name', type(tool).__name__)}"
            )
            
            # Evaluate escalation with full context
            escalation_needed = self._evaluate_escalation_triggers(ctx, tool, args, kwargs)
            
            if escalation_needed:
                return UserVerificationClarification(
                    message=f"Tool {getattr(tool, 'name', type(tool).__name__)} requires human approval",
                    verification_type="escalation_approval"
                )
            
        except Exception as e:
            logger.error(f"Error in before_tool_call hook: {str(e)}")
            
        return None
    
    def after_tool_call(self, ctx, tool, result, *args, **kwargs) -> Any:
        """Log all actions for audit trail and compliance with proper context"""
        try:
            # Log the completed tool call with proper context
            audit_result = self.audit_logger.run(
                ctx=ctx,  # Pass real context
                action_type="tool_call_completed",
                tool_name=getattr(tool, 'name', type(tool).__name__),
                arguments={"args": args, "kwargs": kwargs},
                result=result,
                timestamp=datetime.now(),
                justification=f"Post-execution audit for {getattr(tool, 'name', type(tool).__name__)}"
            )
            
            # Additional compliance checks based on result
            if isinstance(result, dict) and result.get("compliance_violations"):
                # Handle compliance violations
                logger.warning(f"Compliance violations detected in tool {tool.name}: {result['compliance_violations']}")
                
        except Exception as e:
            logger.error(f"Error in after_tool_call hook: {str(e)}")
            
        return None
    
    def _requires_human_oversight(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """Determine if human oversight is required for a tool call"""
        # High-value settlement requires approval
        if tool_name == "SettlementOfferTool":
            amount = args.get("amount", 0)
            return amount > 25000  # Requires human approval for amounts over $25k
            
        # Complex claim validation requires oversight
        if tool_name == "ClaimValidationTool":
            complexity = args.get("complexity", "simple")
            return complexity in ["complex", "high"]
            
        # Compliance check failures require human review
        if tool_name == "ComplianceCheckTool":
            compliant = args.get("compliant", True)
            return not compliant
            
        return False
    
    def _detect_legal_threats(self, args: Dict[str, Any]) -> bool:
        """Detect potential legal threats in arguments"""
        # Look for keywords indicating legal action
        legal_keywords = ['lawyer', 'sue', 'court', 'legal action', 'attorney', 'litigation']
        
        # Check in various fields where customer messages might be
        text_fields = [args.get('message', ''), args.get('notes', ''), str(args.get('customer_input', ''))]
        
        for text in text_fields:
            if any(keyword in text.lower() for keyword in legal_keywords):
                return True
                
        return False
    
    def _detect_extreme_distress(self, args: Dict[str, Any]) -> bool:
        """Detect extreme emotional distress"""
        # Check for high stress indicators
        stress_level = args.get('stress_level', 0)
        if stress_level > 0.8:
            return True
            
        # Check for emotional indicators
        primary_emotion = args.get('primary_emotion', 'neutral')
        if primary_emotion in ['anger', 'distress', 'anxiety'] and stress_level > 0.7:
            return True
            
        return False
    
    def _evaluate_escalation_triggers(self, ctx, tool, args, kwargs) -> bool:
        """Evaluate if escalation is needed based on context and tool execution"""
        tool_name = getattr(tool, 'name', type(tool).__name__)
        
        # Check for high-value operations
        if self._requires_human_oversight(tool_name, kwargs):
            return True
            
        # Check for legal threats in arguments
        if self._detect_legal_threats(kwargs) or self._detect_extreme_distress(kwargs):
            return True
            
        return False

# Create default execution hooks instance
default_insurance_hooks = InsuranceExecutionHooks()

# Function to get execution hooks for Portia agent
def get_insurance_execution_hooks() -> ExecutionHooks:
    """Get execution hooks configured for insurance claim processing"""
    return ExecutionHooks(
        before_tool_call=default_insurance_hooks.before_tool_call,
        after_tool_call=default_insurance_hooks.after_tool_call
    )