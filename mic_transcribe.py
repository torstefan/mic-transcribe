#!/usr/bin/env python3
"""
Whisper Microphone Transcription Tool
-------------------------------------
Records audio while Super_L (Windows/Meta key) is pressed,
then transcribes it using Whisper and simulates typing the text.
"""

import os
import sys
import time
import tempfile
import subprocess
import threading
import signal
import wave
import json
import argparse
from datetime import datetime

# Path to the virtual environment's Python
VENV_PYTHON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "whisper_env", "bin", "python")

try:
    import whisper
    import numpy as np
    import sounddevice as sd
    from pynput import keyboard
    import pyperclip  # For clipboard handling
except ImportError:
    print("Installing required packages...")
    subprocess.run([VENV_PYTHON, "-m", "pip", "install", "pyperclip", "pynput", "sounddevice", "numpy"])
    print("Please install portaudio19-dev and python3-pyaudio system packages:")
    print("sudo apt-get install portaudio19-dev python3-pyaudio")
    print("Then run this script again.")
    sys.exit(1)

class AudioRecorder:
    def __init__(self, model_name="medium", device_index=None, sample_rate=16000, 
               terminal_mode=False, language=None):
        self.recording = False
        self.audio_data = []
        self.sample_rate = sample_rate
        self.model_name = model_name
        self.device_index = device_index
        self.temp_dir = tempfile.mkdtemp()
        self.model = None
        self.terminal_mode = terminal_mode
        self.language = language
        
        # Map of language codes
        self.language_codes = {
            "english": "en",
            "norwegian": "no"
        }
        
        # Load audio devices
        self.list_audio_devices()
        
        # Initialize key listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        
        print(f"Initialized with model: {model_name}")
        print(f"Terminal mode: {'Enabled' if terminal_mode else 'Disabled'}")
        if self.language:
            lang_code = self.language_codes.get(self.language.lower(), self.language)
            print(f"Language: {self.language} (code: {lang_code})")
        else:
            print("Language: Auto-detect")
        print("Press and hold Super_L key (Windows/Meta key) to record, release to transcribe")

    def list_audio_devices(self):
        """List available audio input devices"""
        devices = sd.query_devices()
        print("\nAvailable audio input devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        
        if self.device_index is None:
            default_device = sd.query_devices(kind='input')
            self.device_index = sd.default.device[0]
            print(f"\nUsing default input device: [{self.device_index}] {default_device['name']}")
        
    def on_key_press(self, key):
        try:
            if key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:  # Super_L/Windows/Meta key
                if not self.recording:
                    self.start_recording()
        except Exception as e:
            print(f"Key press error: {e}")
            
    def on_key_release(self, key):
        try:
            if key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:  # Super_L/Windows/Meta key
                if self.recording:
                    self.stop_recording()
        except Exception as e:
            print(f"Key release error: {e}")
    
    def start_recording(self):
        """Start recording audio"""
        print("\nRecording... (release keys to stop)")
        self.recording = True
        self.audio_data = []
        
        # Start recording in a separate thread
        self.record_thread = threading.Thread(target=self._record)
        self.record_thread.daemon = True
        self.record_thread.start()
    
    def _record(self):
        """Recording thread function"""
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, 
                               callback=self._audio_callback, device=self.device_index):
                while self.recording:
                    time.sleep(0.1)
        except Exception as e:
            print(f"Recording error: {e}")
            self.recording = False
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio data"""
        if status:
            print(f"Audio callback status: {status}")
        if self.recording:
            self.audio_data.append(indata.copy())
    
    def stop_recording(self):
        """Stop recording and process the audio"""
        if not self.recording:
            return
            
        print("Processing audio...")
        self.recording = False
        
        # Wait for recording thread to finish
        if hasattr(self, 'record_thread') and self.record_thread.is_alive():
            self.record_thread.join(timeout=1.0)
        
        # Process recorded audio
        if len(self.audio_data) > 0:
            try:
                # Convert recorded audio to numpy array
                audio = np.concatenate(self.audio_data, axis=0).flatten()
                
                # Check if audio is too short
                if len(audio) < self.sample_rate * 0.5:  # Less than 0.5 seconds
                    print("Recording too short, ignoring.")
                    return
                
                # Save audio to temporary WAV file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_wav = os.path.join(self.temp_dir, f"recording_{timestamp}.wav")
                self._save_wav(temp_wav, audio)
                
                # Transcribe audio
                text = self.transcribe(temp_wav)
                
                # Insert text via clipboard
                if text and text.strip():
                    print(f"Transcribed: {text}")
                    self.insert_text(text)
                else:
                    print("No transcription result.")
                    
            except Exception as e:
                print(f"Error processing audio: {e}")
        else:
            print("No audio data recorded.")
    
    def _save_wav(self, filename, audio):
        """Save audio data to WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        print(f"Audio saved to {filename}")
    
    def transcribe(self, audio_file):
        """Transcribe audio using Whisper"""
        try:
            # Load model on first use
            if self.model is None:
                print(f"Loading Whisper model '{self.model_name}'...")
                self.model = whisper.load_model(self.model_name)
                print("Model loaded.")
            
            # Prepare transcription options
            options = {}
            
            # Add language if specified
            if self.language:
                lang_code = self.language_codes.get(self.language.lower(), self.language)
                options["language"] = lang_code
                print(f"Transcribing in {self.language}")
            
            # Transcribe audio with options
            result = self.model.transcribe(audio_file, **options)
            
            # If language was auto-detected, show it
            if not self.language and "language" in result:
                print(f"Detected language: {result['language']}")
                
            return result["text"]
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def insert_text(self, text):
        """Insert transcribed text into the active window"""
        try:
            # Copy text to clipboard
            pyperclip.copy(text)
            print("Text copied to clipboard")
            
            if self.terminal_mode:
                # For terminals, type the text directly character by character
                # This avoids the ^[[200~ bracket paste markers
                for char in text:
                    subprocess.run(["xdotool", "type", char], check=False)
                    # Small delay to avoid overwhelming the terminal
                    time.sleep(0.001)
            else:
                # Regular applications - use clipboard paste
                subprocess.run(["xdotool", "key", "ctrl+v"], check=False)
            
        except Exception as e:
            print(f"Error inserting text: {e}")
            print("Please install xdotool: sudo apt-get install xdotool")
            print("Text is available in clipboard for manual pasting.")
    
    def run(self):
        """Start the recorder"""
        try:
            # Start listener
            self.keyboard_listener.start()
            
            print("Listener started. Press Ctrl+C to exit.")
            
            # Keep the program running
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nExiting...")
                
        except Exception as e:
            print(f"Runtime error: {e}")
        finally:
            # Stop listener
            self.keyboard_listener.stop()
            print("Stopped.")

def main():
    parser = argparse.ArgumentParser(description="Whisper Microphone Transcription Tool")
    parser.add_argument("--model", type=str, default="medium", 
                        choices=["tiny", "base", "small", "medium", "large", "turbo"],
                        help="Whisper model to use (default: medium)")
    parser.add_argument("--device", type=int, default=None, 
                        help="Audio input device index (default: system default)")
    parser.add_argument("--sample-rate", type=int, default=16000,
                        help="Audio sample rate (default: 16000)")
    parser.add_argument("--list-devices", action="store_true",
                        help="List available audio devices and exit")
    parser.add_argument("--debug", action="store_true",
                        help="Print key codes for debugging hotkeys")
    parser.add_argument("--terminal", action="store_true",
                        help="Enable terminal mode (avoids formatting characters in terminals)")
    parser.add_argument("--language", type=str, default=None,
                        choices=["english", "norwegian", "auto"],
                        help="Language for transcription (default: auto-detect)")
    
    args = parser.parse_args()
    
    # Handle language auto setting
    language = args.language
    if language == "auto":
        language = None
    
    if args.debug:
        print("Debug mode: Press keys to see their key codes (Ctrl+C to exit)")
        with keyboard.Listener(on_press=lambda k: print(f"Key pressed: {k}"), 
                               on_release=lambda k: print(f"Key released: {k}")) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nExiting debug mode...")
        return
    
    if args.list_devices:
        devices = sd.query_devices()
        print("Available audio input devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        return
    
    recorder = AudioRecorder(
        model_name=args.model,
        device_index=args.device,
        sample_rate=args.sample_rate,
        terminal_mode=args.terminal,
        language=language
    )
    recorder.run()

if __name__ == "__main__":
    main()