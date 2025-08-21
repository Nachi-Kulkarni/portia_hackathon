import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.voice.hume_integration import HumeEmotionAnalysisTool, VoiceResponseGeneratorTool, EmotionAnalysisResult

class TestHumeEmotionAnalysisTool:
    
    @pytest.mark.asyncio
    async def test_emotion_analysis_mock_angry(self, mock_environment):
        """Test emotion analysis with angry customer"""
        tool = HumeEmotionAnalysisTool()
        mock_ctx = Mock()
        
        result = await tool.run(mock_ctx, "angry customer complaint", "wav")
        
        assert isinstance(result, EmotionAnalysisResult)
        assert result.primary_emotion == "anger"
        assert result.stress_level > 0.5
        assert result.intervention_recommended is True
        assert "angry" in result.transcript.lower()
    
    @pytest.mark.asyncio
    async def test_emotion_analysis_mock_sad(self, mock_environment):
        """Test emotion analysis with sad customer"""
        tool = HumeEmotionAnalysisTool()
        mock_ctx = Mock()
        
        result = await tool.run(mock_ctx, "sad customer loss", "wav")
        
        assert isinstance(result, EmotionAnalysisResult)
        assert result.primary_emotion == "sadness"
        assert result.stress_level > 0.5
        assert result.intervention_recommended is False
        assert "sad" in result.transcript.lower()
    
    @pytest.mark.asyncio
    async def test_emotion_analysis_mock_neutral(self, mock_environment):
        """Test emotion analysis with neutral customer"""
        tool = HumeEmotionAnalysisTool()
        mock_ctx = Mock()
        
        result = await tool.run(mock_ctx, "neutral customer inquiry", "wav")
        
        assert isinstance(result, EmotionAnalysisResult)
        assert result.primary_emotion == "neutral"
        assert result.stress_level < 0.5
        assert result.intervention_recommended is False
    
    @pytest.mark.asyncio
    async def test_emotion_analysis_error_fallback(self, mock_environment):
        """Test error handling falls back to mock data"""
        tool = HumeEmotionAnalysisTool()
        tool.use_mock = False  # Force real API path
        mock_ctx = Mock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            result = await tool.run(mock_ctx, "test audio", "wav")
            
            # Should fall back to mock data
            assert isinstance(result, EmotionAnalysisResult)
            assert result.primary_emotion == "neutral"

class TestVoiceResponseGeneratorTool:
    
    @pytest.mark.asyncio
    async def test_response_generation_empathetic(self):
        """Test empathetic response generation"""
        tool = VoiceResponseGeneratorTool()
        mock_ctx = Mock()
        
        result = await tool.run(
            mock_ctx, 
            "Your claim has been approved for $15,000.", 
            "empathetic"
        )
        
        assert "difficult situation" in result["response_text"]
        assert result["suggested_tone"] == "warm and supportive"
        assert result["emotion_adaptation"] == "empathetic"
        assert result["estimated_speech_duration"] > 0
    
    @pytest.mark.asyncio
    async def test_response_generation_professional(self):
        """Test professional response generation"""
        tool = VoiceResponseGeneratorTool()
        mock_ctx = Mock()
        
        result = await tool.run(
            mock_ctx,
            "Your claim is under review.",
            "professional"
        )
        
        assert "Thank you for contacting us" in result["response_text"]
        assert result["suggested_tone"] == "professional and clear"
        assert result["emotion_adaptation"] == "professional"
    
    @pytest.mark.asyncio
    async def test_response_generation_reassuring(self):
        """Test reassuring response generation"""
        tool = VoiceResponseGeneratorTool()
        mock_ctx = Mock()
        
        result = await tool.run(
            mock_ctx,
            "We will resolve this quickly.",
            "reassuring"
        )
        
        assert "don't worry" in result["response_text"]
        assert result["suggested_tone"] == "calming and confident"
        assert result["emotion_adaptation"] == "reassuring"
    
    @pytest.mark.asyncio
    async def test_response_generation_default(self):
        """Test default response generation"""
        tool = VoiceResponseGeneratorTool()
        mock_ctx = Mock()
        
        result = await tool.run(
            mock_ctx,
            "Standard message.",
            "unknown_emotion"
        )
        
        # Should default to professional
        assert "Thank you for contacting us" in result["response_text"]
        assert result["suggested_tone"] == "professional and clear"