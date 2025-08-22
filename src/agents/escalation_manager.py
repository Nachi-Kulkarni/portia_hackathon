# Apply compatibility fix for Python < 3.12 BEFORE importing Portia
try:
    import src.compatibility_fix  # This patches typing.override
except ImportError:
    pass  # Continue without compatibility fix

from portia.clarification import (
    ActionClarification, 
    UserVerificationClarification,
    MultipleChoiceClarification
)
from dataclasses import dataclass
from typing import Dict, List, Callable, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class EscalationContext:
    """Context for making escalation decisions"""
    conversation_history: List[dict]
    emotion_analysis: dict
    claim_details: dict
    settlement_amount: float
    legal_indicators: List[str]
    compliance_flags: List[str]
    customer_id: str

class EscalationManager:
    """Advanced escalation system with Portia integration"""
    
    # Multi-dimensional escalation triggers
    TRIGGERS = {
        'legal_threat': {
            'keywords': ['lawyer', 'sue', 'court', 'legal action', 'attorney', 'litigation'],
            'threshold': 1,  # Any keyword triggers
            'severity': 'high'
        },
        'extreme_distress': {
            'emotion_check': lambda emotions: emotions.get('distress', 0) > 0.8 or emotions.get('anger', 0) > 0.9,
            'threshold': 0.8,
            'severity': 'high'
        },
        'high_value': {
            'amount_check': lambda amount: amount > 50000,
            'threshold': 50000,
            'severity': 'medium'
        },
        'fraud_suspicion': {
            'confidence_check': lambda confidence: confidence > 0.7,
            'threshold': 0.7,
            'severity': 'high'
        },
        'regulatory_violation': {
            'compliance_check': lambda violations: len(violations) > 0,
            'threshold': 0,
            'severity': 'critical'
        }
    }
    
    def evaluate_escalation_need(self, context: EscalationContext) -> Dict[str, Any]:
        """Comprehensive escalation evaluation"""
        triggered_reasons = []
        severity_score = 0
        
        # Check each trigger type
        for trigger_type, config in self.TRIGGERS.items():
            if self._check_trigger(trigger_type, context, config):
                triggered_reasons.append(trigger_type)
                severity_score += self._get_severity_score(config['severity'])
        
        return {
            'should_escalate': len(triggered_reasons) > 0,
            'triggered_reasons': triggered_reasons,
            'severity_score': severity_score,
            'escalation_type': self._determine_escalation_type(triggered_reasons)
        }
    
    def create_escalation_clarification(self, context: EscalationContext, reasons: List[str]) -> ActionClarification:
        """Generate appropriate Portia clarification for escalation"""
        
        if 'regulatory_violation' in reasons:
            return UserVerificationClarification(
                user_guidance="CRITICAL: Regulatory compliance issue detected. This claim requires immediate supervisor review and legal department approval before proceeding.",
                require_confirmation=True
            )
        
        if 'legal_threat' in reasons:
            return ActionClarification(
                user_guidance=f"Legal escalation triggered. Customer mentioned: {', '.join(context.legal_indicators)}. Transferring to legal-trained senior agent.",
                action_url="/transfer-to-legal-specialist",
                require_confirmation=True
            )
        
        if 'extreme_distress' in reasons:
            return MultipleChoiceClarification(
                user_guidance="High emotional distress detected. How would you like to proceed?",
                choices=[
                    "Transfer to senior empathy-trained agent",
                    "Offer immediate supervisor callback", 
                    "Provide crisis support resources",
                    "Continue with enhanced emotional support protocol"
                ]
            )
        
        # Default escalation
        return ActionClarification(
            user_guidance=f"Escalation triggered due to: {', '.join(reasons)}. Human oversight required.",
            action_url="/escalate-to-supervisor"
        )
    
    def create_handoff_package(self, context: EscalationContext, plan_run=None) -> Dict[str, Any]:
        """Comprehensive context preservation for human agent"""
        return {
            'handoff_timestamp': datetime.now().isoformat(),
            'escalation_reasons': self.evaluate_escalation_need(context)['triggered_reasons'],
            'customer_profile': {
                'customer_id': context.customer_id,
                'emotional_state': context.emotion_analysis,
                'communication_preferences': self._analyze_communication_style(context),
                'stress_indicators': self._extract_stress_indicators(context)
            },
            'claim_summary': {
                'claim_id': context.claim_details.get('claim_id'),
                'claim_type': context.claim_details.get('claim_type'),
                'current_offer': context.settlement_amount,
                'negotiation_history': self._summarize_negotiation(context),
                'compliance_status': context.compliance_flags
            },
            'conversation_analysis': {
                'full_transcript': context.conversation_history,
                'key_moments': self._identify_key_moments(context),
                'sentiment_timeline': self._create_sentiment_timeline(context)
            },
            'agent_recommendations': {
                'suggested_approach': self._recommend_human_strategy(context),
                'risk_factors': self._identify_risk_factors(context),
                'success_probability': self._calculate_success_probability(context)
            },
            'audit_trail': plan_run.outputs.get_audit_log() if plan_run and hasattr(plan_run, 'outputs') else [],
            'regulatory_notes': self._generate_regulatory_summary(context)
        }
    
    def _check_trigger(self, trigger_type: str, context: EscalationContext, config: dict) -> bool:
        """Check if specific trigger condition is met"""
        try:
            if trigger_type == 'legal_threat':
                conversation_text = ' '.join([msg.get('text', '') for msg in context.conversation_history])
                return any(keyword.lower() in conversation_text.lower() for keyword in config['keywords'])
            
            elif trigger_type == 'extreme_distress':
                # Check if emotion_check function exists in config
                if 'emotion_check' in config:
                    return config['emotion_check'](context.emotion_analysis)
                return False
            
            elif trigger_type == 'high_value':
                # Check if amount_check function exists in config
                if 'amount_check' in config:
                    return config['amount_check'](context.settlement_amount)
                return False
            
            elif trigger_type == 'fraud_suspicion':
                # Check if confidence_check function exists in config
                if 'confidence_check' in config:
                    # Get fraud risk score from claim details
                    fraud_score = context.claim_details.get('fraud_risk_score', 0)
                    return config['confidence_check'](fraud_score)
                return False
            
            elif trigger_type == 'regulatory_violation':
                # Check if compliance_check function exists in config
                if 'compliance_check' in config:
                    return config['compliance_check'](context.compliance_flags)
                return False
            
            return False
        except Exception as e:
            logger.error(f"Error checking trigger {trigger_type}: {str(e)}")
            return False
    
    def _get_severity_score(self, severity: str) -> int:
        """Convert severity level to numeric score"""
        severity_map = {'low': 1, 'medium': 3, 'high': 5, 'critical': 10}
        return severity_map.get(severity, 1)
    
    def _determine_escalation_type(self, reasons: List[str]) -> str:
        """Determine the type of escalation based on triggered reasons"""
        if 'regulatory_violation' in reasons:
            return 'compliance_escalation'
        elif 'legal_threat' in reasons:
            return 'legal_escalation'  
        elif 'extreme_distress' in reasons:
            return 'emotional_support_escalation'
        elif 'fraud_suspicion' in reasons:
            return 'fraud_investigation_escalation'
        else:
            return 'general_escalation'
    
    # Helper methods for creating handoff package
    def _analyze_communication_style(self, context: EscalationContext) -> Dict[str, Any]:
        """Analyze customer's communication style"""
        # This would analyze the conversation history to determine communication preferences
        return {
            "preferred_channel": "phone",
            "response_speed": "moderate",
            "formality_level": "standard"
        }
    
    def _extract_stress_indicators(self, context: EscalationContext) -> List[str]:
        """Extract stress indicators from emotional analysis"""
        indicators = []
        if context.emotion_analysis:
            # Check for high stress levels
            if context.emotion_analysis.get('stress_level', 0) > 0.7:
                indicators.append("high_stress")
            
            # Check for negative emotions
            negative_emotions = ['anger', 'distress', 'anxiety', 'frustration']
            for emotion in negative_emotions:
                if context.emotion_analysis.get(emotion, 0) > 0.6:
                    indicators.append(emotion)
        
        return indicators
    
    def _summarize_negotiation(self, context: EscalationContext) -> List[Dict[str, Any]]:
        """Summarize key negotiation points"""
        # This would extract key points from the conversation history
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "summary": "Initial claim review and settlement discussion",
                "key_points": ["customer emotional state", "policy verification", "settlement amount"]
            }
        ]
    
    def _identify_key_moments(self, context: EscalationContext) -> List[Dict[str, Any]]:
        """Identify key moments in the conversation"""
        # This would analyze the conversation to identify important moments
        return [
            {
                "moment_type": "emotional_peak",
                "timestamp": datetime.now().isoformat(),
                "description": "Customer expressed high emotional distress"
            }
        ]
    
    def _create_sentiment_timeline(self, context: EscalationContext) -> List[Dict[str, Any]]:
        """Create a timeline of sentiment changes"""
        # This would create a timeline based on emotional analysis throughout the conversation
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "emotion": context.emotion_analysis.get('primary_emotion', 'neutral') if context.emotion_analysis else 'neutral',
                "stress_level": context.emotion_analysis.get('stress_level', 0) if context.emotion_analysis else 0
            }
        ]
    
    def _recommend_human_strategy(self, context: EscalationContext) -> str:
        """Recommend approach for human agent"""
        # Based on the escalation reasons, recommend an approach
        reasons = self.evaluate_escalation_need(context)['triggered_reasons']
        if 'extreme_distress' in reasons:
            return "Use empathetic communication and provide emotional support"
        elif 'legal_threat' in reasons:
            return "Document all communication and follow legal protocols"
        elif 'high_value' in reasons:
            return "Follow high-value claim procedures and obtain necessary approvals"
        else:
            return "Standard escalation with full context provided"
    
    def _identify_risk_factors(self, context: EscalationContext) -> List[str]:
        """Identify risk factors for the claim"""
        risks = []
        # Add risks based on context
        if context.emotion_analysis and context.emotion_analysis.get('stress_level', 0) > 0.8:
            risks.append("high_emotional_distress")
        
        if context.settlement_amount > 50000:
            risks.append("high_value_claim")
            
        if context.legal_indicators:
            risks.append("potential_legal_action")
            
        return risks
    
    def _calculate_success_probability(self, context: EscalationContext) -> float:
        """Calculate probability of successful resolution"""
        # This would be a more complex calculation based on various factors
        # For now, we'll use a simple heuristic
        base_probability = 0.7  # Start with 70% base probability
        
        # Adjust based on stress level (higher stress = lower success probability)
        if context.emotion_analysis:
            stress_level = context.emotion_analysis.get('stress_level', 0)
            base_probability -= stress_level * 0.3  # Up to 30% reduction for high stress
            
        # Adjust for high-value claims (more complex = slightly lower probability)
        if context.settlement_amount > 50000:
            base_probability -= 0.1  # 10% reduction for high-value claims
            
        # Adjust for legal indicators (lower probability)
        if context.legal_indicators:
            base_probability -= 0.2  # 20% reduction if legal action is mentioned
            
        # Ensure probability stays between 0 and 1
        return max(0.1, min(0.95, base_probability))
    
    def _generate_regulatory_summary(self, context: EscalationContext) -> str:
        """Generate regulatory compliance summary"""
        if context.compliance_flags:
            return f"Compliance issues detected: {', '.join(context.compliance_flags)}. Requires regulatory review."
        else:
            return "No immediate regulatory compliance issues detected."
    
    def evaluate(self, emotion_result: Dict, claim_data: Dict, analysis_result: Dict) -> Dict:
        """Simplified evaluate method for direct use by ClaimNegotiationAgent"""
        escalation_triggers = []
        should_escalate = False
        
        # Define escalation thresholds
        escalation_thresholds = {
            'stress_level': 0.7,
            'anger_level': 0.8,
            'claim_amount': 100000,
            'legal_keywords': ['lawyer', 'attorney', 'legal action', 'sue']
        }
        
        # Check emotional stress
        if emotion_result.get('stress_level', 0) > escalation_thresholds['stress_level']:
            escalation_triggers.append("High customer stress detected")
            should_escalate = True
        
        # Check for anger
        if emotion_result.get('anger', 0) > escalation_thresholds['anger_level']:
            escalation_triggers.append("High anger level detected") 
            should_escalate = True
        
        # Check claim amount
        if claim_data.get('estimated_amount', 0) > escalation_thresholds['claim_amount']:
            escalation_triggers.append("High-value claim requires review")
            should_escalate = True
        
        # Check for legal threats
        transcript = emotion_result.get('transcript', '').lower()
        if any(keyword in transcript for keyword in escalation_thresholds['legal_keywords']):
            escalation_triggers.append("Legal threat detected")
            should_escalate = True
        
        return {
            'should_escalate': should_escalate,
            'escalation_triggers': escalation_triggers,
            'urgency_level': self._calculate_urgency_simple(escalation_triggers),
            'recommended_action': self._get_recommended_action_simple(escalation_triggers)
        }
    
    def _calculate_urgency_simple(self, triggers):
        """Calculate urgency level based on number of triggers"""
        if len(triggers) >= 3:
            return "critical"
        elif len(triggers) >= 2:
            return "high" 
        elif len(triggers) >= 1:
            return "medium"
        return "low"
    
    def _get_recommended_action_simple(self, triggers):
        """Get recommended action based on triggers"""
        if any("legal" in trigger.lower() for trigger in triggers):
            return "Immediate supervisor and legal review required"
        elif len(triggers) >= 2:
            return "Supervisor review required"
        else:
            return "Continue with enhanced monitoring"