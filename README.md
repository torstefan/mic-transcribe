# Whisper Microphone Transcription Tool

A command-line tool that records audio from your microphone when you press the Super key (Windows/Meta key), transcribes it using OpenAI's Whisper speech recognition model, and pastes the text into your active window.

## Features

- **Real-time transcription** - Press and hold the Super key to record, release to transcribe
- **Multiple languages** - Auto-detect languages or specify English or Norwegian
- **Model selection** - Choose from tiny, base, small, medium, large, or turbo models
- **Terminal mode** - Special mode for pasting into terminal applications
- **Device selection** - Choose from available audio input devices
- **Clipboard integration** - Automatically pastes text or copies to clipboard

## Requirements

- Python 3.6+
- OpenAI Whisper
- PyAudio and PortAudio
- xdotool (for Linux)
- Additional Python packages: numpy, sounddevice, pynput, pyperclip

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/whisper-mic-transcribe.git
   cd whisper-mic-transcribe
   ```

2. Create a virtual environment:
   ```
   python -m venv whisper_env
   source whisper_env/bin/activate
   ```

3. Install required packages:
   ```
   pip install openai-whisper pyperclip pynput sounddevice numpy
   ```

4. Install system dependencies (Ubuntu/Debian):
   ```
   sudo apt-get install portaudio19-dev python3-pyaudio xdotool
   ```

## Usage

Basic usage:
```
python mic_transcribe.py
```

### Command-line options:

- `--model [tiny|base|small|medium|large|turbo]` - Select Whisper model (default: medium)
- `--device INDEX` - Specify audio input device index
- `--sample-rate RATE` - Set audio sample rate (default: 16000)
- `--list-devices` - List available audio input devices and exit
- `--debug` - Print key codes for debugging hotkeys
- `--terminal` - Enable terminal mode for pasting into terminal applications
- `--language [english|norwegian|auto]` - Set language for transcription (default: auto-detect)

### Examples:

List available audio devices:
```
python mic_transcribe.py --list-devices
```

Use a specific model and device:
```
python mic_transcribe.py --model small --device 2
```

Transcribe in English using terminal mode:
```
python mic_transcribe.py --language english --terminal
```

## How it works

1. Press and hold the Super key (Windows/Meta key)
2. Speak clearly into your microphone
3. Release the Super key when finished speaking
4. The tool transcribes your speech using Whisper
5. The transcribed text is automatically pasted into your active window

## Notes

- The first transcription may take a moment as the Whisper model is loaded
- Recording quality depends on your microphone and environment
- For better results in noisy environments, use a closer microphone
- Recordings are temporarily saved in a temp directory

## License

MIT License

Copyright (c) 2025 [Your Name or Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.