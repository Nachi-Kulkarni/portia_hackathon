"""
Day 2 Helper Methods for ClaimNegotiationAgent
=============================================

This file contains the Day 2 enhancement methods that integrate with the Day 1 foundation.
These methods handle escalation evaluation, enhanced response generation, and audit trail creation.
"""

from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def _evaluate_escalation_needs(self, emotion_result: Dict[str, Any], 
                              claim_data: Dict[str, Any], 
                              analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Day 2: Evaluate if escalation is needed based on emotion, claim details, and analysis"""
    try:
        from src.agents.escalation_manager import EscalationContext
        
        # Create escalation context
        escalation_context = EscalationContext(
            conversation_history=[],  # Would be populated in real scenario
            emotion_analysis=emotion_result.get("emotion_scores", {}),
            claim_details=claim_data,
            settlement_amount=analysis_result.get("settlement_offer", {}).get("amount", 0),
            legal_indicators=[],  # Would be extracted from conversation
            compliance_flags=analysis_result.get("compliance", {}).get("violations", []),
            customer_id=claim_data.get("customer_id", "unknown")
        )
        
        # Evaluate escalation need
        escalation_evaluation = self.escalation_manager.evaluate_escalation_need(escalation_context)
        
        # Add escalation details if needed
        if escalation_evaluation["should_escalate"]:
            escalation_evaluation["handoff_package"] = self.escalation_manager.create_handoff_package(
                escalation_context, None  # Would pass plan_run in real scenario
            )
        
        logger.info(f"Escalation evaluation: {escalation_evaluation['should_escalate']} - Reasons: {escalation_evaluation['triggered_reasons']}")
        
        return escalation_evaluation
        
    except Exception as e:
        logger.error(f"Escalation evaluation failed: {str(e)}")
        return {
            "should_escalate": False,
            "triggered_reasons": [],
            "severity_score": 0,
            "error": str(e)
        }

def _generate_enhanced_response(self, emotion_result: Dict[str, Any],
                               analysis_result: Dict[str, Any],
                               escalation_result: Dict[str, Any]) -> Dict[str, Any]:
    """Day 2: Generate emotion-aware response with escalation context"""
    try:
        from src.voice.emotion_analyzer import EmotionalContext
        
        # Create emotional context
        emotional_context = EmotionalContext(
            primary_emotion=emotion_result.get("primary_emotion", "neutral"),
            stress_level=emotion_result.get("stress_level", 0.3),
            confidence=emotion_result.get("confidence", 0.7),
            emotion_scores=emotion_result.get("emotion_scores", {})
        )
        
        # Get response strategy
        response_strategy = self.emotion_analyzer.get_response_strategy(emotional_context)
        
        # Generate base response based on analysis
        settlement_offer = analysis_result.get("settlement_offer", {})
        base_response = f"Based on our analysis, we can offer ${settlement_offer.get('amount', 0):,.2f} for your claim."
        
        # Adapt response to emotion
        adapted_response = self.emotion_analyzer.adapt_response_to_emotion(
            base_response, emotional_context
        )
        
        # Add escalation context if needed
        if escalation_result.get("should_escalate"):
            adapted_response += " I'm connecting you with a specialist who can provide additional assistance."
        
        enhanced_response = {
            "base_response": base_response,
            "adapted_response": adapted_response,
            "emotional_adaptation": emotional_context.primary_emotion,
            "tone_indicators": response_strategy.get("tone_indicators", []),
            "escalation_included": escalation_result.get("should_escalate", False),
            "response_confidence": emotional_context.confidence
        }
        
        logger.info(f"Enhanced response generated for {emotional_context.primary_emotion} emotion")
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Enhanced response generation failed: {str(e)}")
        return {
            "base_response": "Thank you for contacting us about your claim.",
            "adapted_response": "Thank you for contacting us about your claim.",
            "error": str(e)
        }

def _create_audit_entry(self, claim_data: Dict[str, Any],
                       emotion_result: Dict[str, Any],
                       analysis_result: Dict[str, Any],
                       escalation_result: Dict[str, Any]) -> Any:
    """Day 2: Create comprehensive audit trail entry"""
    try:
        from src.hooks.audit_logger import AuditEntry
        
        # Create comprehensive audit entry
        audit_entry = AuditEntry(
            action_type="complete_claim_negotiation",
            tool_name="ClaimNegotiationAgent",
            arguments={
                "claim_id": claim_data.get("claim_id"),
                "claim_type": claim_data.get("claim_type"),
                "customer_id": claim_data.get("customer_id"),
                "estimated_amount": claim_data.get("estimated_amount")
            },
            result={
                "settlement_offer": analysis_result.get("settlement_offer"),
                "emotional_analysis": emotion_result,
                "escalation_evaluation": escalation_result,
                "policy_verification": analysis_result.get("policy_status"),
                "compliance_status": analysis_result.get("compliance")
            },
            user_id=claim_data.get("customer_id"),
            plan_run_id=analysis_result.get("plan_run_id", "direct-execution"),
            step_index=0,  # Required field
            compliance_flags=analysis_result.get("compliance", {}).get("violations", []),
            risk_indicators=escalation_result.get("triggered_reasons", []),
            justification=f"Automated claim negotiation with Day 2 enhancements - Emotion: {emotion_result.get('primary_emotion', 'neutral')}"
        )
        
        # Log the audit entry
        self.audit_manager.log_action(audit_entry)
        
        logger.info(f"Audit entry created: {audit_entry.entry_id}")
        
        return audit_entry
        
    except Exception as e:
        logger.error(f"Audit entry creation failed: {str(e)}")
        return None

# Add these methods to the ClaimNegotiationAgent class
ClaimNegotiationAgent._evaluate_escalation_needs = _evaluate_escalation_needs
ClaimNegotiationAgent._generate_enhanced_response = _generate_enhanced_response  
ClaimNegotiationAgent._create_audit_entry = _create_audit_entry