from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

class EmotionResponseConfig(BaseModel):
    """Configuration for emotion-aware responses"""
    emotion: str
    response_templates: List[str]
    tone_indicators: List[str]
    escalation_threshold: float

class EmotionalContext(BaseModel):
    """Context for emotional response adaptation"""
    primary_emotion: str
    stress_level: float
    confidence: float
    emotion_scores: Dict[str, float]

class EmotionAnalyzer:
    """Analyze emotions and provide appropriate response strategies"""
    
    def __init__(self):
        self.response_configs = self._load_response_configs()
    
    def _load_response_configs(self) -> List[EmotionResponseConfig]:
        """Load emotion response configurations"""
        # Default configurations for different emotional states
        configs = [
            EmotionResponseConfig(
                emotion="anger",
                response_templates=[
                    "I understand you're frustrated with this situation.",
                    "I can hear your concern and want to help resolve this.",
                    "Let's work together to address your specific concerns."
                ],
                tone_indicators=["calm", "understanding", "solution-focused"],
                escalation_threshold=0.8
            ),
            EmotionResponseConfig(
                emotion="sadness",
                response_templates=[
                    "I'm truly sorry for what you're going through.",
                    "This must be a difficult time for you and your family.",
                    "I'm here to support you through this process."
                ],
                tone_indicators=["empathetic", "gentle", "supportive"],
                escalation_threshold=0.7
            ),
            EmotionResponseConfig(
                emotion="anxiety",
                response_templates=[
                    "I can see you're worried about this claim.",
                    "Let me walk you through what happens next.",
                    "I'll make sure to keep you informed every step of the way."
                ],
                tone_indicators=["reassuring", "clear", "patient"],
                escalation_threshold=0.6
            ),
            EmotionResponseConfig(
                emotion="neutral",
                response_templates=[
                    "Thank you for contacting us about your claim.",
                    "I'm here to help you with your insurance needs.",
                    "Let's review your claim details together."
                ],
                tone_indicators=["professional", "clear", "helpful"],
                escalation_threshold=0.5
            )
        ]
        return configs
    
    def get_response_strategy(self, emotional_context: EmotionalContext) -> Dict[str, Any]:
        """Get appropriate response strategy based on emotional context"""
        # Find matching emotion config
        config = next((c for c in self.response_configs if c.emotion == emotional_context.primary_emotion), 
                     self.response_configs[-1])  # Default to neutral
        
        # Check if escalation is needed based on stress level
        needs_escalation = emotional_context.stress_level > config.escalation_threshold
        
        return {
            "response_templates": config.response_templates,
            "tone_indicators": config.tone_indicators,
            "needs_escalation": needs_escalation,
            "escalation_reason": f"High stress level ({emotional_context.stress_level}) for {emotional_context.primary_emotion}" if needs_escalation else None
        }
    
    def adapt_response_to_emotion(self, base_response: str, emotional_context: EmotionalContext) -> str:
        """Adapt a response based on detected emotional context"""
        strategy = self.get_response_strategy(emotional_context)
        
        # Use the first template as prefix
        if strategy["response_templates"]:
            adapted_response = f"{strategy['response_templates'][0]} {base_response}"
        else:
            adapted_response = base_response
            
        return adapted_response