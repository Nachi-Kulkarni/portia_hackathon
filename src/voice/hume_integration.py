from portia.tool import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
import os
import httpx
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class EmotionAnalysisResult(BaseModel):
    """Emotion analysis result model"""
    primary_emotion: str = Field(description="Primary detected emotion")
    emotion_scores: Dict[str, float] = Field(description="All emotion scores")
    stress_level: float = Field(description="Calculated stress level (0-1)")
    confidence: float = Field(description="Analysis confidence score")
    transcript: str = Field(description="Speech-to-text transcript")
    intervention_recommended: bool = Field(description="Whether human intervention is recommended")

class HumeEmotionAnalysisArgs(BaseModel):
    """Arguments for Hume emotion analysis"""
    audio_data: str = Field(description="Audio data to analyze")
    audio_format: str = Field(default="wav", description="Audio format (wav, mp3, etc.)")

class HumeEmotionAnalysisTool(Tool):
    """Portia tool for Hume AI emotion analysis"""
    
    def __init__(self):
        # Initialize the Tool with required parameters
        super().__init__(
            id="hume_emotion_analysis",
            name="Hume Emotion Analysis",
            description="Analyze customer emotion from voice input using Hume AI",
            args_schema=HumeEmotionAnalysisArgs,
            output_schema=("json", "Emotion analysis result including primary emotion, scores, and transcript")
        )
        
        # Store Hume API credentials (these will be set as attributes, not fields)
        self._hume_api_key = os.getenv("HUME_API_KEY")
        self._hume_secret_key = os.getenv("HUME_SECRET_KEY")
        
        if not self._hume_api_key or not self._hume_secret_key:
            logger.warning("Hume AI keys not found. Tool will use mock data.")
            self._use_mock = True
        else:
            self._use_mock = False
    
    def run(self, ctx: ToolRunContext, audio_data: str, audio_format: str = "wav") -> EmotionAnalysisResult:
        """Analyze emotion from audio data"""
        try:
            if self._use_mock:
                return self._generate_mock_emotion_analysis(audio_data)
            
            # Real Hume AI integration
            return self._analyze_with_hume_ai(audio_data, audio_format)
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {str(e)}")
            # Fallback to mock data on error
            return self._generate_mock_emotion_analysis(audio_data)
    
    def _analyze_with_hume_ai(self, audio_data: str, audio_format: str) -> EmotionAnalysisResult:
        """Real Hume AI emotion analysis"""
        headers = {
            "X-Hume-Api-Key": self._hume_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "data": [{"data": audio_data, "type": f"audio/{audio_format}"}],
            "models": {
                "prosody": {},
                "language": {}
            }
        }
        
        try:
            # For now, we'll return mock data since we don't have real API access
            # In a real implementation, this would call the Hume API
            return self._generate_mock_emotion_analysis(audio_data)
        except Exception as e:
            logger.error(f"Hume API error: {str(e)}")
            # Fallback to mock data on error
            return self._generate_mock_emotion_analysis(audio_data)
    
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

class VoiceResponseGeneratorArgs(BaseModel):
    """Arguments for voice response generation"""
    message: str = Field(description="Message to generate response for")
    target_emotion: str = Field(default="empathetic", description="Target emotion for the response")

class VoiceResponseGeneratorTool(Tool):
    """Generate emotionally appropriate voice responses"""
    
    def __init__(self):
        # Initialize the Tool with required parameters
        super().__init__(
            id="voice_response_generator",
            name="Voice Response Generator",
            description="Generate emotionally appropriate voice responses for customer interactions",
            args_schema=VoiceResponseGeneratorArgs,
            output_schema=("json", "Generated voice response with emotional adaptation")
        )
    
    def run(self, ctx: ToolRunContext, message: str, target_emotion: str = "empathetic") -> Dict[str, str]:
        """Generate voice response adapted to emotional context"""
        
        # Emotional response templates
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
        
        # Construct emotionally appropriate response
        response = f"{template['prefix']} {message}"
        
        return {
            "response_text": response,
            "suggested_tone": template["tone"],
            "emotion_adaptation": target_emotion,
            "estimated_speech_duration": len(response.split()) * 0.6  # Rough estimate
        }