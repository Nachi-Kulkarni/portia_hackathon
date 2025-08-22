from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
import os
from typing import Optional
import httpx
import json
from datetime import datetime
from src.config import HUME_CONFIG
from src.utils.exceptions import HumeAPIError, AudioProcessingError

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
        """Real Hume AI emotion analysis using official SDK"""
        
        try:
            # Try to use official Hume AI SDK
            return self._analyze_with_hume_sdk(audio_data, audio_format)
        except ImportError:
            logger.warning("Hume AI SDK not available, falling back to direct API calls")
            return self._analyze_with_direct_api(audio_data, audio_format)
        except Exception as e:
            logger.error(f"Hume SDK error: {str(e)}, falling back to mock")
            return self._generate_mock_emotion_analysis(audio_data)
    
    def _analyze_with_hume_sdk(self, audio_data: str, audio_format: str) -> EmotionAnalysisResult:
        """Use official Hume AI Python SDK"""
        try:
            # Try different import patterns for Hume SDK
            try:
                from hume import HumeClient
            except ImportError:
                try:
                    from hume.client import HumeClient
                except ImportError:
                    # If HumeClient not available, fall back to direct API
                    logger.warning("HumeClient not available, falling back to direct API")
                    return self._analyze_with_direct_api(audio_data, audio_format)
            
            import base64
            import tempfile
            import time
            
            # Configure client using the correct pattern
            client = HumeClient(api_key=self._hume_api_key)
            
            # Decode and save audio to temporary file
            audio_bytes = base64.b64decode(audio_data)
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Use start_inference_job_from_local_file as shown in the docs
            file_obj = File.from_path(temp_file_path)
            
            job_id = client.expression_measurement.batch.start_inference_job_from_local_file(
                file=[file_obj],
                json={
                    "models": {
                        "prosody": {},  # Voice emotion analysis
                        "language": {}  # Text analysis with transcript
                    },
                    "transcription": {
                        "language": "en"
                    }
                }
            )
            
            # Poll for completion using configurable limits
            max_polls = HUME_CONFIG.JOB_POLL_MAX_ATTEMPTS
            poll_interval = HUME_CONFIG.JOB_POLL_INTERVAL_SECONDS
            
            logger.info(f"Starting Hume job polling: max {max_polls} attempts, {poll_interval}s intervals")
            
            for attempt in range(max_polls):
                job_status = client.expression_measurement.batch.get_job_details(job_id)
                
                # Check job state using the correct attribute
                if hasattr(job_status, 'state') and job_status.state == "COMPLETED":
                    # Get predictions
                    predictions = client.expression_measurement.batch.get_job_predictions(job_id)
                    
                    # Clean up temp file
                    import os
                    os.unlink(temp_file_path)
                    
                    return self._parse_hume_sdk_response(predictions)
                
                elif hasattr(job_status, 'state') and job_status.state in ["FAILED", "CANCELED"]:
                    error_msg = f"Hume job {job_id} failed with state: {job_status.state}"
                    logger.error(error_msg)
                    raise HumeAPIError(error_msg)
                
                if attempt < max_polls - 1:  # Don't sleep on last attempt
                    time.sleep(poll_interval)
            
            # Cleanup on timeout/failure
            import os
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
            timeout_msg = f"Hume analysis timed out after {max_polls} attempts"
            logger.warning(timeout_msg)
            # Still return mock data for graceful degradation
            return self._generate_mock_emotion_analysis(audio_data)
            
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"Hume SDK not available: {str(e)}, falling back to direct API")
            return self._analyze_with_direct_api(audio_data, audio_format)
        except HumeAPIError as e:
            logger.error(f"Hume API error: {str(e)}, falling back to mock")
            return self._generate_mock_emotion_analysis(audio_data)
        except Exception as e:
            logger.error(f"Unexpected Hume SDK error: {str(e)}, falling back to mock")
            return self._generate_mock_emotion_analysis(audio_data)
    
    def _analyze_with_direct_api(self, audio_data: str, audio_format: str) -> EmotionAnalysisResult:
        """Direct API calls as fallback"""
        try:
            import base64
            import requests
            
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Hume AI Expression Measurement API endpoint
            url = "https://api.hume.ai/v0/batch/jobs"
            
            headers = {
                "X-Hume-Api-Key": self._hume_api_key,
            }
            
            # Create job for emotion analysis
            job_data = {
                "models": {
                    "prosody": {},
                    "language": {}
                },
                "transcription": {
                    "language": "en"
                }
            }
            
            files = {
                "json": (None, json.dumps(job_data), "application/json"),
                "file": ("audio.wav", audio_bytes, "audio/wav")
            }
            
            # Submit job with configurable timeout
            timeout = HUME_CONFIG.HUME_API_TIMEOUT
            logger.debug(f"Submitting Hume API job with {timeout}s timeout")
            response = requests.post(url, headers=headers, files=files, timeout=timeout)
            
            if response.status_code == 201:
                job_info = response.json()
                job_id = job_info.get("job_id")
                
                # Poll for results (simplified for MVP - in production would be async)
                result = self._poll_hume_results(job_id, headers)
                if result:
                    return self._parse_hume_response(result, audio_data)
            
            logger.warning(f"Hume API returned status {response.status_code}, falling back to mock")
            return self._generate_mock_emotion_analysis(audio_data)
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Hume API timeout after {HUME_CONFIG.HUME_API_TIMEOUT}s: {str(e)}")
            return self._generate_mock_emotion_analysis(audio_data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Hume API request failed: {str(e)}")
            return self._generate_mock_emotion_analysis(audio_data)
        except Exception as e:
            logger.error(f"Unexpected direct API error: {str(e)}, falling back to mock")
            return self._generate_mock_emotion_analysis(audio_data)
    
    def _parse_hume_sdk_response(self, predictions) -> EmotionAnalysisResult:
        """Parse Hume SDK response into our standard format"""
        try:
            # Extract first prediction
            if not predictions or len(predictions) == 0:
                return self._generate_mock_emotion_analysis("")
            
            prediction = predictions[0]
            
            # Get prosody (voice emotion) predictions
            prosody_predictions = []
            if hasattr(prediction.models, 'prosody') and prediction.models.prosody:
                prosody_predictions = prediction.models.prosody.grouped_predictions
            
            # Get language (transcript) predictions
            transcript = "[Transcript unavailable]"
            if hasattr(prediction.models, 'language') and prediction.models.language:
                lang_predictions = prediction.models.language.grouped_predictions
                if lang_predictions and len(lang_predictions) > 0:
                    if hasattr(lang_predictions[0], 'predictions') and lang_predictions[0].predictions:
                        transcript = lang_predictions[0].predictions[0].text or transcript
            
            # Process emotion scores from prosody
            emotion_scores = {}
            primary_emotion = "neutral"
            max_score = 0
            
            if prosody_predictions and len(prosody_predictions) > 0:
                if hasattr(prosody_predictions[0], 'predictions') and prosody_predictions[0].predictions:
                    for pred in prosody_predictions[0].predictions:
                        if hasattr(pred, 'emotions'):
                            for emotion in pred.emotions:
                                emotion_name = emotion.name.lower()
                                score = emotion.score
                                emotion_scores[emotion_name] = score
                                
                                if score > max_score:
                                    max_score = score
                                    primary_emotion = emotion_name
            
            # Calculate stress level from negative emotions
            stress_indicators = ["anxiety", "anger", "distress", "fear", "sadness"]
            stress_level = sum(emotion_scores.get(emotion, 0) for emotion in stress_indicators) / len(stress_indicators)
            
            # Determine if intervention is recommended
            intervention_recommended = (
                stress_level > 0.7 or 
                emotion_scores.get("anger", 0) > 0.6 or 
                emotion_scores.get("distress", 0) > 0.6
            )
            
            return EmotionAnalysisResult(
                primary_emotion=primary_emotion,
                emotion_scores=emotion_scores,
                stress_level=min(stress_level, 1.0),
                confidence=max_score,
                transcript=transcript,
                intervention_recommended=intervention_recommended
            )
            
        except Exception as e:
            logger.error(f"Error parsing Hume SDK response: {str(e)}")
            return self._generate_mock_emotion_analysis("")
    
    def _poll_hume_results(self, job_id: str, headers: dict, max_polls: int = None) -> dict:
        """Poll Hume API for job completion with configurable limits"""
        import time
        import requests
        
        if max_polls is None:
            max_polls = HUME_CONFIG.JOB_POLL_MAX_ATTEMPTS
        
        poll_interval = HUME_CONFIG.JOB_POLL_INTERVAL_SECONDS
        results_timeout = HUME_CONFIG.HUME_RESULTS_TIMEOUT
        
        logger.info(f"Polling Hume results for job {job_id}: {max_polls} max attempts")
        
        for attempt in range(max_polls):
            try:
                status_url = f"https://api.hume.ai/v0/batch/jobs/{job_id}"
                response = requests.get(status_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    job_status = response.json()
                    
                    if job_status.get("state") == "COMPLETED":
                        # Get results
                        results_url = f"https://api.hume.ai/v0/batch/jobs/{job_id}/predictions"
                        results_response = requests.get(results_url, headers=headers, timeout=results_timeout)
                        
                        if results_response.status_code == 200:
                            return results_response.json()
                    
                    elif job_status.get("state") in ["FAILED", "CANCELED"]:
                        logger.error(f"Hume job {job_id} failed: {job_status.get('message', 'Unknown error')}")
                        break
                
                if attempt < max_polls - 1:  # Don't sleep on last attempt
                    time.sleep(poll_interval)
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout polling Hume job {job_id} on attempt {attempt + 1}: {str(e)}")
                if attempt == max_polls - 1:  # Last attempt
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error polling Hume job {job_id}: {str(e)}")
                break
            except Exception as e:
                logger.error(f"Unexpected error polling Hume job {job_id}: {str(e)}")
                break
        
        return None
    
    def _parse_hume_response(self, hume_results: dict, audio_data: str) -> EmotionAnalysisResult:
        """Parse Hume API response into our standard format"""
        try:
            # Extract predictions from Hume response
            predictions = hume_results.get("predictions", [{}])[0]
            prosody_predictions = predictions.get("models", {}).get("prosody", {}).get("grouped_predictions", [{}])[0]
            language_predictions = predictions.get("models", {}).get("language", {}).get("grouped_predictions", [{}])[0]
            
            # Get emotion scores from prosody (voice tone)
            prosody_emotions = prosody_predictions.get("predictions", [{}])[0].get("emotions", [])
            
            # Get transcript from language model
            transcript_data = language_predictions.get("predictions", [{}])[0]
            transcript = transcript_data.get("text", "[Transcript unavailable]")
            
            # Find primary emotion (highest score)
            primary_emotion = "neutral"
            emotion_scores = {}
            max_score = 0
            
            for emotion in prosody_emotions:
                emotion_name = emotion.get("name", "unknown")
                score = emotion.get("score", 0)
                emotion_scores[emotion_name] = score
                
                if score > max_score:
                    max_score = score
                    primary_emotion = emotion_name
            
            # Calculate stress level from specific emotions
            stress_indicators = ["Anxiety", "Anger", "Distress", "Fear", "Sadness"]
            stress_level = sum(emotion_scores.get(emotion, 0) for emotion in stress_indicators) / len(stress_indicators)
            
            # Determine if intervention is recommended
            intervention_recommended = (
                stress_level > 0.7 or 
                emotion_scores.get("Anger", 0) > 0.6 or 
                emotion_scores.get("Distress", 0) > 0.6
            )
            
            return EmotionAnalysisResult(
                primary_emotion=primary_emotion.lower(),
                emotion_scores=emotion_scores,
                stress_level=min(stress_level, 1.0),
                confidence=max_score,
                transcript=transcript,
                intervention_recommended=intervention_recommended
            )
            
        except Exception as e:
            logger.error(f"Error parsing Hume response: {str(e)}")
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
    """Generate emotionally appropriate voice responses with optional synthesis"""
    
    def __init__(self):
        # Initialize the Tool with required parameters
        super().__init__(
            id="voice_response_generator",
            name="Voice Response Generator",
            description="Generate emotionally appropriate voice responses for customer interactions",
            args_schema=VoiceResponseGeneratorArgs,
            output_schema=("json", "Generated voice response with emotional adaptation")
        )
        
        self._synthesis_enabled = os.getenv("ENABLE_VOICE_SYNTHESIS", "false").lower() == "true"
    
    def run(self, ctx: ToolRunContext, message: str, target_emotion: str = "empathetic") -> Dict[str, str]:
        """Generate voice response adapted to emotional context"""
        
        # Emotional response templates
        templates = {
            "empathetic": {
                "prefix": "I understand this is a difficult situation for you.",
                "tone": "warm and supportive",
                "voice_params": {"speed": 0.9, "pitch": "medium", "volume": "soft"}
            },
            "professional": {
                "prefix": "Thank you for contacting us regarding your claim.",
                "tone": "professional and clear",
                "voice_params": {"speed": 1.0, "pitch": "medium", "volume": "normal"}
            },
            "reassuring": {
                "prefix": "Please don't worry, we're here to help resolve this matter.",
                "tone": "calming and confident",
                "voice_params": {"speed": 0.8, "pitch": "low", "volume": "soft"}
            },
            "apologetic": {
                "prefix": "I sincerely apologize for any inconvenience this has caused.",
                "tone": "apologetic and understanding",
                "voice_params": {"speed": 0.85, "pitch": "medium-low", "volume": "soft"}
            },
            "urgent": {
                "prefix": "I understand this requires immediate attention.",
                "tone": "urgent but controlled",
                "voice_params": {"speed": 1.1, "pitch": "medium-high", "volume": "normal"}
            }
        }
        
        template = templates.get(target_emotion, templates["professional"])
        
        # Construct emotionally appropriate response
        response_text = f"{template['prefix']} {message}"
        
        # Generate audio if synthesis is enabled
        audio_file = None
        if self._synthesis_enabled:
            audio_file = self._synthesize_speech(response_text, template['voice_params'])
        
        return {
            "response_text": response_text,
            "suggested_tone": template["tone"],
            "emotion_adaptation": target_emotion,
            "estimated_speech_duration": len(response_text.split()) * 0.6,
            "voice_parameters": template['voice_params'],
            "audio_file": audio_file,
            "synthesis_enabled": self._synthesis_enabled
        }
    
    def _synthesize_speech(self, text: str, voice_params: Dict) -> Optional[str]:
        """Synthesize speech using TTS (Text-to-Speech)"""
        try:
            # Try using system TTS first (cross-platform)
            return self._synthesize_with_system_tts(text, voice_params)
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            return None
    
    def _synthesize_with_system_tts(self, text: str, voice_params: Dict) -> Optional[str]:
        """Use system TTS for speech synthesis"""
        try:
            import platform
            import subprocess
            import tempfile
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Use macOS built-in TTS
                voice_rate = int(200 * voice_params.get("speed", 1.0))
                cmd = ["say", "-r", str(voice_rate), "-o", temp_filename, text]
                subprocess.run(cmd, check=True, capture_output=True)
                
            elif system == "Windows":
                # Use Windows SAPI TTS (requires PowerShell)
                ps_script = f"""
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synth.SetOutputToWaveFile('{temp_filename}')
                $synth.Speak('{text}')
                $synth.Dispose()
                """
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                
            elif system == "Linux":
                # Use espeak or festival if available
                try:
                    speed = int(175 * voice_params.get("speed", 1.0))
                    cmd = ["espeak", "-s", str(speed), "-w", temp_filename, text]
                    subprocess.run(cmd, check=True, capture_output=True)
                except FileNotFoundError:
                    # Fallback to festival
                    cmd = ["text2wave", "-o", temp_filename]
                    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, check=True)
                    process.communicate(input=text.encode())
            
            # Verify file was created
            if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                return temp_filename
            else:
                return None
                
        except Exception as e:
            logger.error(f"System TTS synthesis failed: {str(e)}")
            return None