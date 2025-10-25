"""
Audio Controller for text-to-speech and speech recognition.
Uses macOS 'say' command for TTS and speech_recognition for microphone input.
"""

import subprocess
import threading
from typing import Optional, Callable


# Voice configurations
NARRATOR_VOICE = "Samantha"
COMPANION_VOICE = "Alex"


class AudioController:
    """Controls text-to-speech and speech recognition."""
    
    def __init__(self):
        """Initialize AudioController."""
        self.is_speaking = False
        self.current_process: Optional[subprocess.Popen] = None
        self._stop_requested = False
    
    def speak(self, text: str, voice: str = NARRATOR_VOICE, blocking: bool = False):
        """
        Speak text using macOS say command.
        
        Args:
            text: Text to speak
            voice: Voice to use (default: NARRATOR_VOICE)
            blocking: If True, wait for speech to complete
        """
        if self._stop_requested:
            self._stop_requested = False
            return
        
        self.is_speaking = True
        
        try:
            if blocking:
                subprocess.run(['say', '-v', voice, text], check=True)
                self.is_speaking = False
            else:
                self.current_process = subprocess.Popen(['say', '-v', voice, text])
                # Monitor completion in background
                def monitor():
                    if self.current_process:
                        self.current_process.wait()
                        self.is_speaking = False
                
                thread = threading.Thread(target=monitor, daemon=True)
                thread.start()
        except Exception as e:
            self.is_speaking = False
            raise Exception(f"Failed to speak: {e}")
    
    def stop_speaking(self):
        """Stop current speech."""
        self._stop_requested = True
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self.current_process.wait()
        self.is_speaking = False
    
    def speak_as_narrator(self, text: str, blocking: bool = False):
        """
        Speak text as narrator.
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        self.speak(text, NARRATOR_VOICE, blocking)
    
    def speak_as_companion(self, text: str, blocking: bool = False):
        """
        Speak text as companion.
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        self.speak(text, COMPANION_VOICE, blocking)
    
    def listen_for_wake_word(self, timeout: int = 1) -> bool:
        """
        Listen for wake word "hey companion".
        
        Args:
            timeout: Seconds to listen
            
        Returns:
            True if wake word detected
        """
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
                text = recognizer.recognize_sphinx(audio)
                return "hey companion" in text.lower() or "companion" in text.lower()
        except Exception:
            # Timeout or recognition error
            return False
    
    def capture_question(self, timeout: int = 10) -> str:
        """
        Capture a question from microphone.
        
        Args:
            timeout: Maximum seconds to listen
            
        Returns:
            Transcribed text
        """
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                return recognizer.recognize_sphinx(audio)
        except Exception as e:
            raise Exception(f"Failed to capture question: {e}")
