from portia import Portia, Config
from portia.tool_registry import ToolRegistry
from portia.execution_hooks import ExecutionHooks
from portia.clarification import ActionClarification, UserVerificationClarification
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BaseInsuranceAgent:
    """Base agent class with Portia SDK integration"""
    
    def __init__(self, agent_name: str = "insurance_agent"):
        self.agent_name = agent_name
        self.config = Config.from_default()
        
        # Initialize Portia with custom tools and hooks
        self.portia = Portia(
            config=self.config,
            tools=self._setup_tool_registry(),
            execution_hooks=self._setup_execution_hooks()
        )
        
        logger.info(f"Initialized {agent_name} with Portia SDK")
    
    def _setup_tool_registry(self) -> ToolRegistry:
        """Configure insurance-specific tool registry"""
        # Import here to avoid circular imports
        from src.tools.policy_tools import PolicyLookupTool
        from src.tools.claim_tools import ClaimValidationTool  
        from src.tools.compliance_tools import ComplianceCheckTool
        
        # Start with empty registry for base implementation
        tools = ToolRegistry()
        
        # Add insurance-specific tools
        custom_tools = [
            PolicyLookupTool(),
            ClaimValidationTool(),
            ComplianceCheckTool()
        ]
        
        for tool in custom_tools:
            tools = tools + ToolRegistry([tool])
        
        return tools
    
    def _setup_execution_hooks(self) -> ExecutionHooks:
        """Configure execution hooks for compliance and escalation"""
        return ExecutionHooks(
            before_tool_call=self._before_tool_call_hook,
            after_tool_call=self._after_tool_call_hook
        )
    
    def _before_tool_call_hook(self, tool, args, plan_run, step):
        """Pre-tool execution compliance and escalation checks"""
        logger.info(f"Executing tool: {tool.name} with args: {args}")
        
        # Check for high-value settlements requiring approval
        if tool.name == "create_settlement_offer" and args.get("amount", 0) > 25000:
            return UserVerificationClarification(
                user_guidance=f"Settlement amount ${args['amount']} exceeds $25,000 threshold. Manager approval required.",
                require_confirmation=True
            )
        
        # Check for emotional distress indicators
        if args.get("customer_emotion") in ["extreme_distress", "threatening"]:
            return ActionClarification(
                user_guidance="Customer showing signs of extreme distress. Immediate human escalation recommended.",
                action_url="/escalate-to-human-agent",
                require_confirmation=True
            )
        
        return None
    
    def _after_tool_call_hook(self, tool, args, result, plan_run, step):
        """Post-tool execution audit logging"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool.name,
            "arguments": args,
            "result_summary": self._summarize_result(result),
            "plan_run_id": str(plan_run.id),
            "step_index": step
        }
        
        # Log to audit trail
        self._log_audit_entry(audit_entry)
        return None
    
    def _summarize_result(self, result) -> str:
        """Create a summary of tool execution result"""
        if isinstance(result, dict):
            return f"Dictionary with {len(result)} keys"
        elif isinstance(result, list):
            return f"List with {len(result)} items"
        elif hasattr(result, '__dict__'):
            return f"{type(result).__name__} object"
        else:
            return str(type(result).__name__)
    
    def _log_audit_entry(self, audit_entry: Dict[str, Any]):
        """Log audit entry for compliance tracking"""
        if os.getenv("ENABLE_AUDIT_LOGGING", "false").lower() == "true":
            audit_file = f"audit_trail_{self.agent_name}.log"
            with open(audit_file, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        
        logger.info(f"Audit: {audit_entry['tool_name']} executed at {audit_entry['timestamp']}")
    
    async def process_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main claim processing method using Portia planning"""
        try:
            # Create detailed processing plan
            plan_description = f"""
            Process insurance claim with the following details:
            - Claim ID: {claim_data.get('claim_id')}
            - Policy Number: {claim_data.get('policy_number')}
            - Claim Type: {claim_data.get('claim_type')}
            - Estimated Amount: ${claim_data.get('estimated_amount', 0)}
            - Customer Emotional State: {claim_data.get('customer_emotion', 'neutral')}
            
            Requirements:
            1. Verify policy coverage and validity
            2. Validate claim authenticity and check for fraud indicators
            3. Calculate appropriate settlement range based on precedents
            4. Generate initial settlement offer
            5. Ensure full regulatory compliance
            6. Escalate to human if necessary
            """
            
            # Generate execution plan
            plan = self.portia.plan(plan_description)
            logger.info(f"Generated plan {plan.id} for claim {claim_data.get('claim_id')}")
            
            # Execute plan with full audit trail
            plan_run = self.portia.run_plan(
                plan, 
                end_user=claim_data.get('customer_id', 'anonymous')
            )
            
            # Extract results and audit data
            result = {
                "claim_id": claim_data.get("claim_id"),
                "processing_status": "completed" if hasattr(plan_run, 'state') and plan_run.state.name == "COMPLETE" else "requires_clarification",
                "settlement_recommendation": getattr(plan_run.outputs, 'final_output', {}).get('value') if hasattr(plan_run, 'outputs') else None,
                "audit_trail": self._extract_audit_trail(plan_run),
                "clarifications_raised": len(getattr(plan_run.outputs, 'clarifications', [])) if hasattr(plan_run, 'outputs') else 0,
                "plan_run_id": str(plan_run.id)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing claim {claim_data.get('claim_id')}: {str(e)}")
            return {
                "claim_id": claim_data.get("claim_id"),
                "processing_status": "error",
                "error_message": str(e)
            }
    
    def _extract_audit_trail(self, plan_run) -> List[Dict[str, Any]]:
        """Extract audit trail from plan run"""
        # This would extract the actual audit information from Portia
        # For now, return basic information
        return [{
            "plan_run_id": str(plan_run.id),
            "status": getattr(plan_run, 'state', {}).get('name', 'unknown') if hasattr(plan_run, 'state') else 'unknown',
            "execution_timestamp": datetime.now().isoformat()
        }]