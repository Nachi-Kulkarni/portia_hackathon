# Apply compatibility fix for Python < 3.12 BEFORE importing anything that uses Portia
try:
    import src.compatibility_fix  # This patches typing.override
except ImportError:
    pass  # Continue without compatibility fix

from portia import Portia, Config
from portia import DefaultToolRegistry, ToolRegistry
from portia.execution_hooks import ExecutionHooks
from portia.clarification import ActionClarification, UserVerificationClarification
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime
import json
from src.hooks.escalation_triggers import get_insurance_execution_hooks

logger = logging.getLogger(__name__)

class BaseInsuranceAgent:
    """Base agent class with Portia SDK integration"""
    
    def __init__(self, agent_name: str = "insurance_agent"):
        self.agent_name = agent_name
        
        # Use explicit configuration to avoid issues with environment variable loading
        portia_api_key = os.getenv('PORTIA_CONFIG__PORTIA_API_KEY')
        openai_api_key = os.getenv('PORTIA_CONFIG__OPENAI_API_KEY')
        default_model = os.getenv('PORTIA_CONFIG__DEFAULT_MODEL', 'gpt-4.1')
        
        if portia_api_key and openai_api_key:
            # Create config with explicit parameters
            self.config = Config(
                portia_api_key=portia_api_key,
                openai_api_key=openai_api_key,
                default_model=default_model,
                openai_model=default_model,
                llm_provider="openai"
            )
        else:
            # Fallback to default config (will work in demo mode)
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
        
        # Add insurance-specific tools
        custom_tools = [
            PolicyLookupTool(),
            ClaimValidationTool(),
            ComplianceCheckTool()
        ]
        
        # Create registry using proper Portia pattern
        base_registry = DefaultToolRegistry(config=self.config)
        tools = base_registry + custom_tools
        
        return tools
    
    def _setup_execution_hooks(self) -> ExecutionHooks:
        """Configure execution hooks for compliance and escalation"""
        # Use our custom insurance execution hooks
        return get_insurance_execution_hooks()
    
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
    
    def _after_tool_call_hook(self, tool, output, plan_run, step):
        """Post-tool execution audit logging"""
        # Extract arguments from the step if available
        args = {}
        if hasattr(step, 'inputs') and step.inputs:
            args = step.inputs
        
        # Convert step to serializable format
        step_index = 0
        if hasattr(step, 'index'):
            step_index = step.index
        elif isinstance(step, int):
            step_index = step
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool.name,
            "arguments": args,
            "result_summary": self._summarize_result(output),
            "plan_run_id": str(plan_run.id),
            "step_index": step_index
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
            try:
                with open(audit_file, "a") as f:
                    f.write(json.dumps(audit_entry, default=str) + "\n")
            except Exception as e:
                logger.error(f"Error writing to audit file: {e}")
        
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
                "processing_status": "completed" if hasattr(plan_run, 'state') and getattr(plan_run.state, 'name', '') == "COMPLETE" else "requires_clarification",
                "settlement_recommendation": getattr(getattr(plan_run, 'outputs', {}), 'final_output', None),
                "audit_trail": self._extract_audit_trail(plan_run),
                "clarifications_raised": len(getattr(getattr(plan_run, 'outputs', {}), 'clarifications', [])) if hasattr(plan_run, 'outputs') else 0,
                "plan_run_id": str(getattr(plan_run, 'id', 'unknown'))
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
            "plan_run_id": str(getattr(plan_run, 'id', 'unknown')),
            "status": getattr(getattr(plan_run, 'state', {}), 'name', 'unknown') if hasattr(plan_run, 'state') else 'unknown',
            "execution_timestamp": datetime.now().isoformat()
        }]


# Enhanced agent with emotion awareness
class EmotionAwareAgent(BaseInsuranceAgent):
    """Enhanced agent with emotion awareness"""
    
    def _setup_tool_registry(self):
        """Add voice and emotion tools to registry"""
        base_tools = super()._setup_tool_registry()
        
        # Import voice tools here to avoid circular imports
        from src.voice.hume_integration import HumeEmotionAnalysisTool, VoiceResponseGeneratorTool
        
        emotion_tools = [
            HumeEmotionAnalysisTool(),
            VoiceResponseGeneratorTool()
        ]
        
        # Add voice tools to the registry
        for tool in emotion_tools:
            base_tools = base_tools + ToolRegistry([tool])
        
        return base_tools
    
    async def process_voice_claim(self, audio_data: str, claim_context: Dict) -> Dict[str, Any]:
        """Process claim with voice emotion analysis"""
        
        # First analyze the emotional context
        emotion_plan = self.portia.plan(
            f"Analyze customer emotion from voice input for claim {claim_context.get('claim_id')}",
            plan_inputs=[{"name": "audio_data", "description": "Audio data to analyze"}]
        )
        emotion_run = self.portia.run_plan(
            emotion_plan,
            plan_run_inputs={"audio_data": audio_data}
        )
        
        # Extract emotion data and incorporate into claim processing
        emotion_result = emotion_run.outputs.final_output.value if hasattr(emotion_run.outputs, 'final_output') and hasattr(emotion_run.outputs.final_output, 'value') else {}
        
        # Enhanced claim data with emotional context
        enhanced_claim_data = {
            **claim_context,
            "customer_emotion": emotion_result.get("primary_emotion", "neutral") if isinstance(emotion_result, dict) else "neutral",
            "stress_level": emotion_result.get("stress_level", 0.5) if isinstance(emotion_result, dict) else 0.5,
            "requires_special_handling": emotion_result.get("intervention_recommended", False) if isinstance(emotion_result, dict) else False
        }
        
        # Process with emotion-aware handling
        return await self.process_claim(enhanced_claim_data)