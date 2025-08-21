import pyaudio
import wave
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MicrophoneRecorder:
    """Record audio from microphone"""  
    def __init__(self, 
                 chunk_size: int = 1024,
                 format_: int = pyaudio.paInt16,
                 channels: int = 1,
                 rate: int = 44100,
                 record_seconds: int = 5):
        """
        Initialize microphone recorder
        
        Args:
            chunk_size: Audio chunk size
            format_: Audio format (pyaudio.paInt16, pyaudio.paFloat32, etc.)
            channels: Number of audio channels (1 for mono, 2 for stereo)
            rate: Sample rate in Hz
            record_seconds: Recording duration in seconds
        """
        self.chunk_size = chunk_size
        self.format = format_
        self.channels = channels
        self.rate = rate
        self.record_seconds = record_seconds
        self.audio = pyaudio.PyAudio()
        
    def record_audio(self) -> Optional[bytes]:
        """
        Record audio from microphone
        
        Returns:
            Audio data as bytes, or None if recording failed
        """
        try:
            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print(f"🎤 Recording for {self.record_seconds} seconds...")
            print("Please speak into your microphone...")
            
            frames = []
            
            # Record audio
            for i in range(0, int(self.rate / self.chunk_size * self.record_seconds)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            print("✅ Recording finished")
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            
            # Convert frames to bytes
            audio_data = b''.join(frames)
            return audio_data
            
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            return None
    
    def record_audio_to_file(self, filename: str) -> bool:
        """
        Record audio from microphone and save to file
        
        Args:
            filename: Output WAV file name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print(f"🎤 Recording for {self.record_seconds} seconds...")
            print("Please speak into your microphone...")
            
            frames = []
            
            # Record audio
            for i in range(0, int(self.rate / self.chunk_size * self.record_seconds)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            print("✅ Recording finished")
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            
            # Save audio to WAV file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            print(f"💾 Audio saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording audio to file: {str(e)}")
            return False
    
    def __del__(self):
        """\"\"\"Clean up audio resources\"\"\""""
        if hasattr(self, 'audio'):
            self.audio.terminate()

def record_customer_voice(record_seconds: int = 5) -> Optional[str]:
    """\"\"\"
    Record customer voice input for insurance claim processing
    
    Args:
        record_seconds: Recording duration in seconds
        
    Returns:
        Audio data as base64 encoded string, or None if recording failed
    """
    try:
        recorder = MicrophoneRecorder(record_seconds=record_seconds)
        audio_data = recorder.record_audio()
        
        if audio_data:
            # Convert to base64 for transmission
            import base64
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            return encoded_audio
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error recording customer voice: {str(e)}")
        return None

def record_voice_to_file(filename: str, record_seconds: int = 5) -> bool:
    """\"\"\"
    Record voice input and save to file
    
    Args:
        filename: Output WAV file name
        record_seconds: Recording duration in seconds
        
    Returns:
        True if successful, False otherwise
    \"\"\""""
    try:
        recorder = MicrophoneRecorder(record_seconds=record_seconds)
        return recorder.record_audio_to_file(filename)
    except Exception as e:
        logger.error(f"Error recording voice to file: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Record voice and get base64 encoded data
    print("Testing microphone recording...")
    audio_data = record_customer_voice(record_seconds=3)
    
    if audio_data:
        print(f"🎤 Recorded audio data length: {len(audio_data)} characters")
        print("✅ Microphone recording test successful")
    else:
        print("❌ Microphone recording failed")
    
    # Record voice to file
    print("\nTesting file recording...")
    success = record_voice_to_file("test_recording.wav", record_seconds=3)
    
    if success:
        print("✅ File recording test successful")
    else:
        print("❌ File recording failed")