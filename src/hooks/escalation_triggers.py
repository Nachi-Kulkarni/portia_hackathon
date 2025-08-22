from portia.execution_hooks import ExecutionHooks
from portia.clarification import ActionClarification, UserVerificationClarification
from src.agents.escalation_manager import EscalationManager, EscalationContext
from src.hooks.audit_logger import AuditLoggerTool
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class InsuranceExecutionHooks:
    """Custom execution hooks for insurance claim processing"""
    
    def __init__(self):
        self.escalation_manager = EscalationManager()
        self.audit_logger = AuditLoggerTool()
    
    def before_tool_call(self, tool, args, plan_run, step) -> Any:
        """Intercept tool calls for compliance and escalation checks"""
        try:
            # Log the tool call attempt
            audit_result = self.audit_logger.run(
                ctx=None,  # In a real implementation, this would be the actual context
                action_type="tool_call_attempt",
                arguments={"tool_name": tool.name, "args": args},
                result=None,
                justification=f"Pre-execution logging for tool {tool.name}"
            )
            
            # Check for escalation triggers based on tool and arguments
            if self._requires_human_oversight(tool.name, args):
                return UserVerificationClarification(
                    user_guidance=f"Human approval required for {tool.name} with settlement amount ${args.get('amount', 'N/A')}",
                    require_confirmation=True
                )
            
            # Check for legal risk indicators
            if self._detect_legal_threats(args) or self._detect_extreme_distress(args):
                return ActionClarification(
                    user_guidance="Human intervention required for sensitive situation. Escalating to senior claims manager.",
                    action_url="/escalate-to-human",
                    require_confirmation=True
                )
            
        except Exception as e:
            logger.error(f"Error in before_tool_call hook: {str(e)}")
            
        return None
    
    def after_tool_call(self, tool, args, result, plan_run, step) -> Any:
        """Log all actions for audit trail and compliance"""
        try:
            # Log the completed tool call
            audit_result = self.audit_logger.run(
                ctx=None,  # In a real implementation, this would be the actual context
                action_type="tool_call_completed",
                arguments={"tool_name": tool.name, "args": args},
                result=result,
                justification=f"Post-execution logging for tool {tool.name}"
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

# Create default execution hooks instance
default_insurance_hooks = InsuranceExecutionHooks()

# Function to get execution hooks for Portia agent
def get_insurance_execution_hooks() -> ExecutionHooks:
    """Get execution hooks configured for insurance claim processing"""
    return ExecutionHooks(
        before_tool_call=default_insurance_hooks.before_tool_call,
        after_tool_call=default_insurance_hooks.after_tool_call
    )