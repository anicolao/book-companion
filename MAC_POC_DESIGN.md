# Mac POC Design: Scrappy Book Companion

## Overview

This design outlines a minimal, scrappy, yet **complete** proof-of-concept for the Book Companion that runs entirely on macOS using only built-in system tools and lightweight dependencies. The goal is to validate the core concept with the simplest possible implementation.

### Core Principle: "Zero Cloud, Maximum Scrappy"

- **No external APIs**: No OpenAI, no cloud LLM services (in v1)
- **Built-in macOS tools**: Use `say` for TTS, `sox` or Python for audio recording
- **Local LLM**: Use Ollama or llama.cpp for local inference
- **Free content**: Project Gutenberg for books
- **Single script**: One Python application that does everything

## Implementation Language: Python 3

**Why Python?**
- Pre-installed on macOS
- Excellent library support for audio, text processing
- Easy integration with command-line tools (`say`, `afplay`)
- Rapid prototyping
- Simple subprocess management for system commands

**Key Dependencies** (minimal):
- **Standard library**: `subprocess`, `os`, `threading`, `queue`
- **gutenbergpy** or **requests**: Fetch books from Project Gutenberg (1-2 dependencies)
- **pyaudio** or **sounddevice**: Microphone input
- **speech_recognition**: Convert speech to text using built-in macOS recognition
- **ollama-python** or direct HTTP calls: Interface with local Ollama LLM

Total external dependencies: ~3-4 lightweight packages

## Feature Set (MVP)

### Essential Features (Must Have)

1. **Book Selection & Loading**
   - Browse/search Project Gutenberg catalog (simple text list)
   - Download and cache book text locally
   - Parse book into manageable chunks (paragraphs or pages)

2. **Text-to-Speech Playback**
   - Use macOS `say` command for narration
   - Read book text paragraph by paragraph
   - Simple playback controls: play, pause, resume, skip forward/back

3. **Voice-Activated Pause**
   - Continuous microphone monitoring while book is playing
   - Detect wake word/phrase (e.g., "Hey companion" or "Question")
   - Pause playback when user speaks

4. **Interactive Q&A**
   - Record user question via microphone
   - Transcribe using macOS built-in speech recognition
   - Send question + book context to local LLM (Ollama)
   - Speak LLM response using `say` with different voice
   - Resume playback when conversation ends

5. **Context Awareness**
   - Track current position in book (paragraph/page number)
   - Include last N paragraphs in LLM context
   - Maintain conversation history for follow-up questions

6. **Session Persistence**
   - Save current position in book
   - Remember which book user is reading
   - Simple JSON file for state management

### Nice-to-Have Features (Deferred)

- AI-initiated pauses
- Multiple book management
- Bookmarks and notes
- GUI interface (start with terminal)
- Chapter navigation
- Reading speed control

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Mac POC Application                       │
│                   (Single Python Script)                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Book       │  │   Audio      │  │  Conversation│      │
│  │   Manager    │  │   Controller │  │   Handler    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────────┐    ┌──────────┐
│   Project   │    │  macOS Built-in │    │  Ollama  │
│  Gutenberg  │    │    say/afplay   │    │  (Local  │
│    API      │    │  SpeechRecog.   │    │   LLM)   │
└─────────────┘    └─────────────────┘    └──────────┘
```

### Data Flow

```
1. Book Playback Loop:
   Gutenberg Text → Chunk Parser → `say` command → Speaker

2. User Interaction:
   Mic Input → Speech Recognition → Text Question
      ↓
   Context Builder (current position + last N paragraphs)
      ↓
   Ollama LLM → Response Text → `say` command → Speaker

3. State Management:
   Current Position → JSON File ← Book ID + Paragraph Index
```

### File Structure

```
book_companion_poc/
├── companion.py              # Main application
├── book_manager.py           # Book downloading and parsing
├── audio_controller.py       # TTS and microphone handling
├── conversation_handler.py   # LLM interaction
├── config.py                 # Configuration and constants
├── requirements.txt          # Python dependencies
├── data/
│   ├── books/                # Downloaded book texts
│   │   └── book_12345.txt
│   └── state.json            # Current session state
└── README_POC.md             # Setup and usage instructions
```

## Technical Implementation Details

### 1. Text-to-Speech (macOS `say`)

```python
# Two different voices for narrator vs. companion
NARRATOR_VOICE = "Samantha"      # Book reading
COMPANION_VOICE = "Alex"         # AI responses

def speak_text(text, voice=NARRATOR_VOICE, wait=True):
    """Use macOS say command for TTS"""
    cmd = ['say', '-v', voice, text]
    if wait:
        subprocess.run(cmd)
    else:
        subprocess.Popen(cmd)
```

### 2. Microphone Input & Speech Recognition

```python
import speech_recognition as sr

def listen_for_wake_word():
    """Continuously listen for wake phrase"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=1)
        try:
            text = recognizer.recognize_sphinx(audio)  # Offline
            # Or recognizer.recognize_google(audio)     # Online fallback
            if "hey companion" in text.lower():
                return True
        except:
            pass
    return False

def record_question():
    """Record and transcribe user question"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=10)
        text = recognizer.recognize_sphinx(audio)
        return text
```

### 3. Local LLM with Ollama

```python
import requests

def ask_llm(question, context):
    """Send query to local Ollama instance"""
    prompt = f"""You are a helpful reading companion. Based on this book excerpt:

{context}

User question: {question}

Provide a clear, concise answer that helps understanding."""

    response = requests.post('http://localhost:11434/api/generate', 
        json={
            'model': 'llama2',  # or phi, mistral, etc.
            'prompt': prompt,
            'stream': False
        })
    return response.json()['response']
```

### 4. Book Management (Project Gutenberg)

```python
import requests
from gutenbergpy.gutenbergcache import GutenbergCache

def search_books(query):
    """Search Gutenberg catalog"""
    # Simple implementation using gutenbergpy
    cache = GutenbergCache.get_cache()
    results = cache.query(query)
    return results

def download_book(book_id):
    """Download book text from Project Gutenberg"""
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    response = requests.get(url)
    with open(f"data/books/book_{book_id}.txt", 'w') as f:
        f.write(response.text)
    return response.text

def parse_into_chunks(text):
    """Split book into paragraphs"""
    # Remove Gutenberg header/footer
    start = text.find("*** START OF")
    end = text.find("*** END OF")
    body = text[start:end] if start > 0 else text
    
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
    return paragraphs
```

### 5. Main Application Loop

```python
class BookCompanion:
    def __init__(self):
        self.current_book = None
        self.current_position = 0
        self.is_playing = False
        self.conversation_active = False
        
    def play_book(self):
        """Main playback loop"""
        while self.current_position < len(self.current_book):
            paragraph = self.current_book[self.current_position]
            
            # Speak paragraph
            self.speak_async(paragraph)
            
            # Monitor for wake word while speaking
            while self.is_speaking():
                if self.listen_for_wake_word():
                    self.pause()
                    self.handle_conversation()
                    break
            
            self.current_position += 1
            self.save_state()
    
    def handle_conversation(self):
        """Manage Q&A interaction"""
        self.speak("Yes? What would you like to discuss?", 
                  voice=COMPANION_VOICE)
        
        question = self.record_question()
        context = self.get_context(lookback=5)  # Last 5 paragraphs
        
        response = ask_llm(question, context)
        self.speak(response, voice=COMPANION_VOICE)
        
        self.speak("Shall we continue reading?", voice=COMPANION_VOICE)
        answer = self.record_question()
        
        if "yes" in answer.lower():
            self.resume()
```

## First Milestone: "Hello Book"

**Goal**: Demonstrate end-to-end flow with a single book

**Deliverables**:
1. Working Python script that can:
   - Download one specific Project Gutenberg book (e.g., "Alice in Wonderland" - Book #11)
   - Read the book aloud using macOS `say`
   - Pause when user says "Hey companion"
   - Answer one simple question about the current context
   - Resume reading after conversation

2. Simple command-line interface:
   ```
   $ python companion.py
   Welcome to Book Companion POC!
   
   Loading "Alice's Adventures in Wonderland"...
   Press Ctrl+C to quit
   
   [Reading] Chapter 1, Paragraph 5...
   "Alice was beginning to get very tired..."
   
   [Wake word detected!]
   Companion: Yes? What would you like to discuss?
   
   User: Who is Alice?
   Companion: Alice is the main character, a young girl who...
   
   Companion: Shall we continue reading?
   User: Yes
   
   [Resuming playback...]
   ```

3. Basic state persistence (JSON file)

4. README with setup instructions

**Success Criteria**:
- Can play audio of book using built-in macOS voice
- Can pause on voice command
- Can answer at least basic questions about current context
- Saves and restores reading position
- Runs entirely locally on a Mac

**Timeline**: 1-2 weeks (20-30 hours)

### Milestone Breakdown

#### Week 1: Foundation (10-15 hours)
- **Days 1-2**: Environment setup
  - Install Ollama and download llama2 model
  - Set up Python virtual environment
  - Install minimal dependencies
  - Test `say` command with different voices
  
- **Days 3-4**: Book loading and TTS
  - Implement Project Gutenberg download
  - Parse book into paragraphs
  - Basic TTS playback with `say`
  - State persistence (save position)

#### Week 2: Interaction (10-15 hours)
- **Days 5-6**: Voice input
  - Implement microphone recording
  - Speech-to-text with built-in recognition
  - Wake word detection
  
- **Days 7-8**: LLM integration
  - Set up Ollama connection
  - Context building (current position + history)
  - Question answering
  - Integration testing

- **Day 9**: Polish and documentation
  - Error handling
  - README with setup steps
  - Demo video/screencast

## Installation & Setup

### Prerequisites
```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Ollama
brew install ollama

# 3. Start Ollama and download model
ollama serve &
ollama pull llama2  # or phi, mistral - ~4GB download

# 4. Install Python dependencies
pip3 install -r requirements.txt
```

### Requirements.txt
```
requests
speech_recognition
pyaudio
gutenbergpy
```

### Running the POC
```bash
python3 companion.py
```

## Constraints & Limitations

### Technical Constraints
- **Playback quality**: macOS `say` is functional but not professional narrator quality
- **Speech recognition**: Built-in recognition may have accuracy issues
- **LLM capability**: Local models are less capable than GPT-4
- **Performance**: LLM inference on CPU may be slow (5-10s per response)
- **Wake word detection**: Simple keyword matching, not sophisticated

### Scope Limitations
- Single book at a time
- No GUI (terminal only)
- No chapter navigation
- No speed control
- No bookmarks beyond position
- No AI-initiated pauses
- No conversation export

### Known Issues
- `say` command blocks execution (need threading)
- Microphone continuous listening drains battery
- Context window limited by local LLM memory
- No handling of network failures

## Future Enhancements (Post-POC)

### V2: Better UX
- Simple GUI with Tkinter or PyQt
- Visual text highlighting (karaoke-style)
- Waveform visualization
- Chapter navigation

### V3: Smarter Companion
- Better wake word detection (Porcupine)
- Conversation memory across sessions
- AI-suggested pauses based on content
- Better context retrieval (semantic search)

### V4: Production Ready
- Support multiple books
- Cloud LLM option (OpenAI API)
- Better TTS (ElevenLabs integration)
- Mobile app (iOS for Mac users)
- Sync across devices

## Open Questions

1. **Voice Quality**: Is macOS `say` good enough for extended listening, or should we use a better TTS from the start?
2. **Wake Word**: "Hey companion" vs. push-to-talk button vs. automatic pause detection?
3. **LLM Choice**: Llama2 (better quality) vs. Phi (faster) vs. Mistral (balanced)?
4. **Book Selection**: Manual entry of Gutenberg ID vs. search interface?
5. **Context Size**: How many paragraphs to include? Impact on response quality vs. speed?

## Success Metrics

### For POC Validation
- [ ] Can listen to 30+ minutes of book without crashes
- [ ] Wake word detection works >80% of the time
- [ ] Q&A responses are relevant and helpful >70% of the time
- [ ] Reading position is correctly saved and restored
- [ ] Setup time < 30 minutes for new user
- [ ] At least 2 people try it and provide feedback

### User Experience Goals
- **Time to first word**: < 5 seconds after starting
- **Wake word response**: < 1 second latency
- **Question answering**: < 15 seconds total (recognize + LLM + speak)
- **Crash recovery**: Automatic resume from last position

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ollama model too slow | High | Start with smallest model (Phi), add better hardware recommendation |
| Speech recognition poor | Medium | Provide fallback to typed input, recommend quiet environment |
| `say` quality insufficient | Medium | Document voice selection, consider quick switch to external TTS |
| Wake word unreliable | Medium | Add keyboard shortcut as backup (spacebar to pause) |
| LLM responses off-topic | Medium | Better prompt engineering, context tuning |
| Python dependency issues | Low | Document exact versions, provide Docker option |

## Conclusion

This Mac POC design focuses on **rapid validation** of the core Book Companion concept using only macOS built-in tools and minimal dependencies. The scrappy approach allows us to:

1. **Test the hypothesis**: Is an interactive audiobook companion valuable?
2. **Learn quickly**: What works and what doesn't in the user experience?
3. **Iterate fast**: Python + system tools = quick changes
4. **Stay focused**: No cloud setup, no complex infrastructure

**The first milestone ("Hello Book")** proves the concept end-to-end with a complete, if basic, experience. Success here validates the approach and informs next steps toward a production application.

## Next Steps

1. **Approve this design**: Review and sign-off on approach
2. **Set up development environment**: Install Ollama, Python deps
3. **Build "Hello Book" milestone**: 1-2 weeks implementation
4. **User testing**: Get 2-3 people to try it
5. **Iterate or pivot**: Based on feedback, refine or rethink

---

**Key Insight**: By using only what's already on a Mac, we minimize setup friction and maximize learning velocity. This POC isn't about production quality—it's about validating that the core interaction (listening + conversing) creates value for users.
