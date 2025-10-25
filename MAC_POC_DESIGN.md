# Mac POC Design: Scrappy Book Companion

## Overview

A minimal proof-of-concept for an interactive audiobook companion that runs entirely on macOS using built-in tools and local AI.

**Core Principle**: "Zero Cloud, Maximum Scrappy"
- macOS `say` for text-to-speech
- Built-in speech recognition for voice input
- Ollama for local LLM inference
- Project Gutenberg for free books
- Terminal UI for interaction

## Implementation Language: Python 3

**Why Python:**
- Excellent TUI library support (Textual, Rich)
- Easy integration with macOS command-line tools (`say`, speech recognition)
- Rapid prototyping
- Strong library ecosystem for audio and text processing

**Dependencies:**
- `textual` - Modern TUI framework
- `requests` - HTTP requests for Project Gutenberg
- `speech_recognition` - Microphone input and transcription
- `pyaudio` - Audio capture
- Direct HTTP calls to Ollama API (no additional package needed)

## POC Features

### Book Selection
- Simple TUI menu to browse Project Gutenberg catalog
- Start with "A Christmas Carol" by Charles Dickens (Book #46)
- Download and cache book text locally

### Playback
- Text-to-speech using macOS `say` command
- Two distinct voices: narrator (reading) and companion (AI responses)
- Display current text being read in TUI
- Simple controls: play, pause, skip forward/back paragraph

### Interaction
- Wake word detection: "Hey companion"
- Voice-to-text question capture
- Context-aware responses from Ollama
- Spoken responses using companion voice
- Resume reading after conversation

### State Management
- Save current reading position
- Persist to simple JSON file
- Auto-resume on restart

## Architecture

```
┌─────────────────────────────────────────┐
│         Textual TUI Application          │
│  (Book Browser, Playback UI, Chat)      │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│        Application Components            │
│                                          │
│  BookManager  AudioController  ChatBot  │
└──┬────────────┬────────────────┬────────┘
   │            │                │
   ▼            ▼                ▼
Project    macOS `say`      Ollama
Gutenberg  + SpeechRecog    (Local)
```

### File Structure

```
book-companion/
├── flake.nix                 # Nix development environment
├── companion.py              # Main TUI application
├── book_manager.py           # Gutenberg download/parsing
├── audio_controller.py       # TTS and microphone
├── chat_bot.py               # Ollama interaction
├── data/
│   ├── books/
│   │   └── christmas_carol.txt
│   └── state.json
└── README.md
```

## Implementation Details

### Text-to-Speech

```python
import subprocess

NARRATOR_VOICE = "Samantha"
COMPANION_VOICE = "Alex"

def speak(text, voice=NARRATOR_VOICE):
    subprocess.run(['say', '-v', voice, text])
```

### Speech Recognition

```python
import speech_recognition as sr

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=1)
        text = recognizer.recognize_sphinx(audio)
        return "hey companion" in text.lower()

def capture_question():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=10)
        return recognizer.recognize_sphinx(audio)
```

### Ollama Integration

```python
import requests

def ask_companion(question, book_context):
    prompt = f"""Based on this excerpt from "A Christmas Carol":

{book_context}

Question: {question}

Provide a helpful answer."""
    
    response = requests.post('http://localhost:11434/api/generate',
        json={
            'model': 'llama2',
            'prompt': prompt,
            'stream': False
        })
    return response.json()['response']
```

### Book Loading

```python
import requests

def download_book(book_id=46):
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    response = requests.get(url)
    return parse_book(response.text)

def parse_book(text):
    # Remove Gutenberg header/footer
    start = text.find("*** START OF")
    end = text.find("*** END OF")
    body = text[start:end] if start > 0 else text
    
    # Split into paragraphs
    return [p.strip() for p in body.split('\n\n') if p.strip()]
```

## Setup and Usage

### Prerequisites
- macOS
- [Nix with flakes enabled](https://nixos.org/download.html)

### Getting Started

```bash
# Clone repository
git clone https://github.com/anicolao/book-companion.git
cd book-companion

# Enter Nix development environment
nix develop

# Start Ollama (first time)
ollama serve &
ollama pull llama2

# Run the companion
python companion.py
```

The Nix flake provides:
- Python 3 with Textual, requests, speech_recognition, pyaudio
- Ollama for local LLM
- Git

### Example Session

```
$ python companion.py

╔══════════════════════════════════════════╗
║     Book Companion - POC v0.1            ║
╠══════════════════════════════════════════╣
║                                          ║
║ Now reading: A Christmas Carol           ║
║ Position: Stave 1, Paragraph 3           ║
║                                          ║
║ "Marley was dead: to begin with..."     ║
║                                          ║
║ [▶ Playing] [⏸ Pause] [⏭ Skip]          ║
╚══════════════════════════════════════════╝

[Wake word detected: "Hey companion"]
Companion: Yes? What would you like to discuss?

You: Who is Marley?

Companion: Marley is Scrooge's deceased business 
partner who has been dead for seven years...

Companion: Shall we continue reading?

You: Yes

[Resuming playback...]
```
