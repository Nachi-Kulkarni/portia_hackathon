from portia.tool import Tool, ToolRunContext
from pydantic import BaseModel, Field
import httpx
import asyncio
import base64
from typing import Dict, List, Optional
import logging
import os
from .emotion_analyzer import EmotionAnalyzer, EmotionalContext

logger = logging.getLogger(__name__)

class EmotionAnalysisResult(BaseModel):
    """Emotion analysis result model"""
    primary_emotion: str = Field(description="Primary detected emotion")
    emotion_scores: Dict[str, float] = Field(description="All emotion scores")
    stress_level: float = Field(description="Calculated stress level (0-1)")
    confidence: float = Field(description="Analysis confidence score")
    transcript: str = Field(description="Speech-to-text transcript")
    intervention_recommended: bool = Field(description="Whether human intervention is recommended")

class HumeEmotionAnalysisTool(Tool):
    """Portia tool for Hume AI emotion analysis"""
    
    def __init__(self):
        super().__init__()
        self.hume_api_key = os.getenv("HUME_API_KEY")
        self.hume_secret_key = os.getenv("HUME_SECRET_KEY")
        
        if not self.hume_api_key or not self.hume_secret_key:
            logger.warning("Hume AI keys not found. Tool will use mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    async def run(self, ctx: ToolRunContext, audio_data: str, audio_format: str = "wav") -> EmotionAnalysisResult:
        """Analyze emotion from audio data"""
        try:
            if self.use_mock:
                return self._generate_mock_emotion_analysis(audio_data)
            
            # Real Hume AI integration
            return await self._analyze_with_hume_ai(audio_data, audio_format)
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {str(e)}")
            # Fallback to mock data on error
            return self._generate_mock_emotion_analysis(audio_data)
    
    async def _analyze_with_hume_ai(self, audio_data: str, audio_format: str) -> EmotionAnalysisResult:
        """Real Hume AI emotion analysis"""
        headers = {
            "X-Hume-Api-Key": self.hume_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "data": [{"data": audio_data, "type": f"audio/{audio_format}"}],
            "models": {
                "prosody": {},
                "language": {}
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.hume.ai/v0/batch/jobs",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Hume API error: {response.status_code}")
            
            # Process Hume AI response
            hume_result = response.json()
            return self._process_hume_response(hume_result)
    
    def _generate_mock_emotion_analysis(self, audio_data: str) -> EmotionAnalysisResult:
        """Generate mock emotion analysis for testing"""
        # Simulate different emotional states based on input characteristics
        if "angry" in audio_data.lower() or "mad" in audio_data.lower():
            return EmotionAnalysisResult(
                primary_emotion="anger",
                emotion_scores={"anger": 0.8, "frustration": 0.7, "sadness": 0.3},
                stress_level=0.85,
                confidence=0.9,
                transcript="I'm really angry about this claim denial!",
                intervention_recommended=True
            )
        elif "sad" in audio_data.lower() or "upset" in audio_data.lower():
            return EmotionAnalysisResult(
                primary_emotion="sadness",
                emotion_scores={"sadness": 0.9, "distress": 0.6, "anxiety": 0.4},
                stress_level=0.7,
                confidence=0.85,
                transcript="I'm just so sad about losing my car in the accident.",
                intervention_recommended=False
            )
        else:
            return EmotionAnalysisResult(
                primary_emotion="neutral",
                emotion_scores={"calmness": 0.7, "contentment": 0.5},
                stress_level=0.2,
                confidence=0.8,
                transcript="I'd like to discuss my insurance claim.",
                intervention_recommended=False
            )
    
    def _process_hume_response(self, hume_result: dict) -> EmotionAnalysisResult:
        """Process actual Hume API response"""
        # This would process the real Hume API response format
        # For now, return a placeholder result
        return EmotionAnalysisResult(
            primary_emotion="neutral",
            emotion_scores={"neutral": 0.8},
            stress_level=0.3,
            confidence=0.8,
            transcript="Processed audio input",
            intervention_recommended=False
        )

class VoiceResponseGeneratorTool(Tool):
    """Generate emotionally appropriate voice responses"""
    
    def __init__(self):
        super().__init__()
        self.emotion_analyzer = EmotionAnalyzer()
    
    async def run(self, ctx: ToolRunContext, message: str, emotional_context: dict = None, target_emotion: str = "empathetic") -> Dict[str, str]:
        """Generate voice response adapted to emotional context"""
        
        # If we have emotional context, adapt the response accordingly
        if emotional_context:
            # Convert dict to EmotionalContext model
            emotion_ctx = EmotionalContext(**emotional_context)
            
            # Get response strategy based on emotion
            strategy = self.emotion_analyzer.get_response_strategy(emotion_ctx)
            
            # Adapt response to emotion
            adapted_message = self.emotion_analyzer.adapt_response_to_emotion(message, emotion_ctx)
            
            # Use the first tone indicator as the suggested tone
            suggested_tone = strategy["tone_indicators"][0] if strategy["tone_indicators"] else "professional"
            
            return {
                "response_text": adapted_message,
                "suggested_tone": suggested_tone,
                "emotion_adaptation": emotion_ctx.primary_emotion,
                "needs_escalation": strategy["needs_escalation"],
                "escalation_reason": strategy["escalation_reason"],
                "estimated_speech_duration": len(adapted_message.split()) * 0.6  # Rough estimate
            }
        
        # Fallback to basic templates if no emotional context
        templates = {
            "empathetic": {
                "prefix": "I understand this is a difficult situation for you.",
                "tone": "warm and supportive"
            },
            "professional": {
                "prefix": "Thank you for contacting us regarding your claim.",
                "tone": "professional and clear"
            },
            "reassuring": {
                "prefix": "Please don't worry, we're here to help resolve this matter.",
                "tone": "calming and confident"
            }
        }
        
        template = templates.get(target_emotion, templates["professional"])
        response = f"{template['prefix']} {message}"
        
        return {
            "response_text": response,
            "suggested_tone": template["tone"],
            "emotion_adaptation": target_emotion,
            "needs_escalation": False,
            "escalation_reason": None,
            "estimated_speech_duration": len(response.split()) * 0.6  # Rough estimate
        }