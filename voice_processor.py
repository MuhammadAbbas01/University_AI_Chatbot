"""
Voice processing for the University of Malakand AI Assistant.

- Speech-to-text: OpenAI Whisper (tiny model) through Hugging Face Transformers
- Text-to-speech: gTTS
"""

import os
import tempfile
import logging
from typing import Dict, Any
import numpy as np
import soundfile as sf
import librosa
from gtts import gTTS
from transformers import pipeline
import torch

class SimpleVoiceProcessor:
    """Speech-to-text (Whisper tiny) and text-to-speech (gTTS)."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.logger.info("=" * 80)
        self.logger.info("🎤 INITIALIZING VOICE SYSTEM")
        self.logger.info("=" * 80)
        
        # Initialize Whisper for speech-to-text (tiny model for speed)
        try:
            self.logger.info("📥 Loading Whisper model (this takes 10-15 seconds)...")
            self.stt_model = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-tiny",  # small and fast
                device=0 if self.device == "cuda" else -1
            )
            self.logger.info("✅ Whisper loaded successfully!")
        except Exception as e:
            self.logger.error(f"❌ Failed to load Whisper: {e}")
            self.stt_model = None
        
        self.logger.info("✅ Voice system ready!")
        self.logger.info("=" * 80)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def speech_to_text(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file.

        Returns a dict: {success, text, error}.
        """
        try:
            if not self.stt_model:
                return {
                    'success': False,
                    'text': '',
                    'error': 'Speech recognition not available'
                }
            
            self.logger.info(f"🎤 Transcribing audio: {audio_file_path}")
            
            # Load audio using librosa (handles WebM, WAV, MP3, etc.)
            audio_data, sample_rate = librosa.load(audio_file_path, sr=16000, mono=True)

            # Normalize audio
            audio_data = librosa.util.normalize(audio_data)

            # Check if audio is too short or empty
            if len(audio_data) < 1600:  # Less than 0.1 seconds
                return {
                    'success': False,
                    'text': '',
                    'error': 'Audio too short or empty'
                }
            
            # Transcribe using Whisper
            result = self.stt_model(
                audio_data,
                return_timestamps=False
            )
            
            text = result['text'].strip()
            
            self.logger.info(f"✅ Transcribed: '{text[:50]}...'")
            
            return {
                'success': True,
                'text': text,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Transcription failed: {e}")
            return {
                'success': False,
                'text': '',
                'error': str(e)
            }
    
    def text_to_speech(self, text: str, output_path: str = None) -> Dict[str, Any]:
        """
        Convert text to an MP3 file with gTTS.

        Returns a dict: {success, file_path, error}.
        """
        try:
            if not text or len(text.strip()) == 0:
                return {
                    'success': False,
                    'file_path': None,
                    'error': 'No text provided'
                }
            
            self.logger.info(f"🔊 Generating speech: '{text[:50]}...'")
            
            # Create output path if not provided
            if not output_path:
                output_path = tempfile.mktemp(suffix='.mp3', prefix='tts_')
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            
            self.logger.info(f"✅ Audio saved to: {output_path}")
            
            return {
                'success': True,
                'file_path': output_path,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"❌ TTS failed: {e}")
            return {
                'success': False,
                'file_path': None,
                'error': str(e)
            }


# ============================================================================
# GLOBAL INSTANCE (Singleton)
# ============================================================================

_voice_processor = None

def get_voice_processor():
    """Get or create voice processor instance"""
    global _voice_processor
    if _voice_processor is None:
        _voice_processor = SimpleVoiceProcessor()
    return _voice_processor


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 TESTING VOICE PROCESSOR")
    print("=" * 80)
    
    processor = get_voice_processor()
    
    # Test TTS
    print("\n📝 Testing Text-to-Speech...")
    test_text = "Welcome to University of Malakand AI Assistant!"
    result = processor.text_to_speech(test_text)
    
    if result['success']:
        print(f"✅ TTS Success! Audio saved to: {result['file_path']}")
        print(f"   File size: {os.path.getsize(result['file_path'])} bytes")
    else:
        print(f"❌ TTS Failed: {result['error']}")
    
    print("\n" + "=" * 80)
    print("✅ VOICE PROCESSOR TEST COMPLETE!")
    print("=" * 80)