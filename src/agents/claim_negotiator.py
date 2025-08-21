from src.agents.base_agent import BaseInsuranceAgent
from src.voice.hume_integration import HumeEmotionAnalysisTool, VoiceResponseGeneratorTool
from src.tools.policy_tools import PolicyLookupTool
from src.tools.claim_tools import ClaimValidationTool
from src.tools.precedent_tools import PrecedentAnalysisTool
from src.tools.compliance_tools import ComplianceCheckTool
from src.tools.settlement_tools import SettlementOfferTool
from portia.tool_registry import ToolRegistry
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaimNegotiationAgent(BaseInsuranceAgent):
    """Complete claim negotiation agent with voice integration"""
    
    def _setup_tool_registry(self) -> ToolRegistry:
        """Configure complete tool suite"""
        base_tools = super()._setup_tool_registry()
        
        specialized_tools = [
            HumeEmotionAnalysisTool(),
            VoiceResponseGeneratorTool(),
            PolicyLookupTool(),
            ClaimValidationTool(), 
            PrecedentAnalysisTool(),
            ComplianceCheckTool(),
            SettlementOfferTool()
        ]
        
        # Combine all tools
        complete_registry = base_tools
        for tool in specialized_tools:
            complete_registry = complete_registry + ToolRegistry([tool])
        
        return complete_registry
    
    async def negotiate_claim_full_pipeline(self, 
                                          audio_data: str,
                                          claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete end-to-end claim negotiation pipeline"""
        
        pipeline_plan = f"""
        Execute complete insurance claim negotiation pipeline:
        
        STEP 1: Voice & Emotion Analysis
        - Analyze customer audio for emotional state and transcript
        - Determine stress level and intervention needs
        
        STEP 2: Policy Verification
        - Look up policy details for {claim_data.get('policy_number')}
        - Verify coverage and policy status
        
        STEP 3: Claim Validation
        - Validate claim authenticity and coverage
        - Assess fraud risk factors
        
        STEP 4: Precedent Analysis  
        - Research similar settlement cases
        - Calculate recommended settlement range
        
        STEP 5: Compliance Check
        - Verify regulatory compliance requirements
        - Identify required approvals
        
        STEP 6: Settlement Offer Generation
        - Create final settlement offer
        - Include emotional context considerations
        
        STEP 7: Response Generation
        - Generate emotionally appropriate response
        - Prepare escalation if needed
        
        Claim Details: {claim_data}
        Audio Data: Will be provided as plan input
        """
        
        try:
            # Execute comprehensive pipeline
            plan = self.portia.plan(
                pipeline_plan,
                plan_inputs=[{"name": "audio_data", "description": "Audio data to analyze"}]
            )
            plan_run = self.portia.run_plan(
                plan,
                end_user=claim_data.get('customer_id', 'anonymous'),
                plan_run_inputs={"audio_data": audio_data}
            )
            
            # Extract comprehensive results
            if hasattr(plan_run, 'state') and plan_run.state.name == "COMPLETE":
                return {
                    "status": "negotiation_complete",
                    "claim_id": claim_data.get("claim_id"),
                    "settlement_offer": getattr(plan_run.outputs, 'final_output', {}).get('value') if hasattr(plan_run, 'outputs') else None,
                    "emotional_analysis": self._extract_emotion_data(plan_run),
                    "compliance_status": self._extract_compliance_data(plan_run),
                    "audit_trail": self._extract_full_audit_trail(plan_run),
                    "plan_run_id": str(plan_run.id),
                    "processing_time_seconds": self._calculate_processing_time(plan_run)
                }
            else:
                clarifications = getattr(plan_run.outputs, 'clarifications', []) if hasattr(plan_run, 'outputs') else []
                return {
                    "status": "requires_clarification",
                    "claim_id": claim_data.get("claim_id"),
                    "clarifications_needed": len(clarifications),
                    "pending_approvals": self._extract_pending_approvals(plan_run),
                    "plan_run_id": str(plan_run.id)
                }
                
        except Exception as e:
            logger.error(f"Pipeline error for claim {claim_data.get('claim_id')}: {str(e)}")
            return {
                "status": "error",
                "claim_id": claim_data.get("claim_id"),
                "error_message": str(e),
                "fallback_action": "escalate_to_human"
            }
    
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
        emotion_result = getattr(emotion_run.outputs, 'final_output', {}).get('value', {}) if hasattr(emotion_run, 'outputs') else {}
        
        # Enhanced claim data with emotional context
        enhanced_claim_data = {
            **claim_context,
            "customer_emotion": emotion_result.get("primary_emotion", "neutral"),
            "stress_level": emotion_result.get("stress_level", 0.5),
            "requires_special_handling": emotion_result.get("intervention_recommended", False)
        }
        
        # Process with emotion-aware handling
        return await self.process_claim(enhanced_claim_data)
    
    def _extract_emotion_data(self, plan_run) -> Dict[str, Any]:
        """Extract emotion analysis data from plan run"""
        # This would extract emotion data from the actual plan execution
        return {
            "primary_emotion": "neutral",
            "stress_level": 0.3,
            "confidence": 0.8
        }
    
    def _extract_compliance_data(self, plan_run) -> Dict[str, Any]:
        """Extract compliance data from plan run"""
        # This would extract compliance information from the plan execution
        return {
            "compliant": True,
            "risk_level": "low",
            "required_approvals": []
        }
    
    def _extract_full_audit_trail(self, plan_run) -> List[Dict[str, Any]]:
        """Extract comprehensive audit trail"""
        # This would extract the complete audit trail from Portia
        return [{
            "plan_run_id": str(plan_run.id),
            "status": getattr(plan_run, 'state', {}).get('name', 'unknown') if hasattr(plan_run, 'state') else 'unknown',
            "execution_timestamp": datetime.now().isoformat(),
            "steps_completed": "all_steps" if hasattr(plan_run, 'state') else "unknown"
        }]
    
    def _calculate_processing_time(self, plan_run) -> float:
        """Calculate processing time for the plan run"""
        # This would calculate actual processing time
        return 5.2  # Mock processing time in seconds
    
    def _extract_pending_approvals(self, plan_run) -> List[str]:
        """Extract pending approvals from plan run"""
        # This would extract actual pending approvals
        return ["senior_manager_review"] if hasattr(plan_run, 'outputs') else []