# Book Companion

An AI-powered audiobook companion that listens and learns alongside you, creating an interactive and enriching reading experience.

## What is Book Companion?

Book Companion is an innovative LLM-based application that transforms passive audiobook listening into an interactive learning experience. Think of it as having a thoughtful reading partner who listens to the audiobook with you, ready to discuss ideas, clarify concepts, and help you deeply engage with the material.

## Key Features

- **Active Listening**: The AI companion listens to the audiobook alongside you, building context and understanding of the content
- **User-Initiated Conversations**: Pause at any time to discuss thoughts, ask questions, or explore ideas from the book
- **AI-Initiated Insights**: The AI can pause the audiobook to share relevant insights, make connections, or suggest points for reflection
- **Learning Optimization**: The companion identifies key moments for discussion to help solidify and expand your understanding
- **Contextual Awareness**: All conversations are grounded in the current position and overall narrative of the audiobook

## How It Works

1. **Start Listening**: Begin playing your audiobook through the Book Companion application
2. **Engage Naturally**: Pause anytime to ask questions or share thoughts about the content
3. **AI Participation**: The AI may also pause to share insights or suggest discussing important concepts
4. **Deep Conversations**: Engage in meaningful dialogue that enhances comprehension and retention
5. **Resume Seamlessly**: Continue listening whenever you're ready

## Use Cases

- **Students**: Deepen understanding of academic texts and prepare for discussions
- **Book Clubs**: Generate discussion points and explore multiple perspectives
- **Lifelong Learners**: Maximize retention and application of non-fiction content
- **Critical Readers**: Analyze themes, characters, and literary techniques in real-time
- **Language Learners**: Clarify vocabulary and cultural context while listening

## Project Status

🎉 **Mac POC is now available!** A minimal proof-of-concept implementation is ready for macOS users. See [MAC_POC_DESIGN.md](MAC_POC_DESIGN.md) for implementation details.

For long-term vision, see [VISION.md](VISION.md) and [DESIGN_SKETCH.md](DESIGN_SKETCH.md) for full technical architecture plans.

## Getting Started

### Mac POC (Proof of Concept)

**Prerequisites:**
- macOS (for `say` command and optimal experience)
- [Nix with flakes enabled](https://nixos.org/download.html)
- Ollama for local AI (installed via Nix)

**Quick Start:**

```bash
# Clone the repository
git clone https://github.com/anicolao/book-companion.git
cd book-companion

# Enter Nix development environment (installs all dependencies)
nix develop

# Start Ollama (in a separate terminal)
ollama serve &
ollama pull llama2

# Run the companion
python companion.py
```

**Features:**
- Terminal-based user interface (TUI) using Textual
- Reads books from Project Gutenberg (currently: "A Christmas Carol")
- Text-to-speech narration using macOS `say` command
- Continuous playback that auto-advances through paragraphs
- Wake word detection for voice interaction with AI companion
- State persistence (remembers your reading position)

**Keyboard Controls:**
- `p` - Play/pause narration
- `n`/`b` - Skip forward/backward by paragraph
- `w` - Toggle wake word detection (say "hey companion" to ask questions)
- `q` - Quit and save position

**Wake Word Interaction:**

1. Press `w` to enable wake word detection
2. Say "hey companion" to pause and trigger interaction
3. Ask your question about the book
4. The AI will respond using context from nearby paragraphs
5. Playback resumes automatically after the response

If wake word detection doesn't work:
- Make sure you have a working microphone
- The app will display error messages in the chat area if there are issues
- All dependencies are installed via Nix, no additional setup needed
- You can still use all other features (TTS playback) without voice input

**Note:** Ollama must be running for AI responses.

## Contributing

We welcome contributions! As this project is in early stages, please check the issues tab for ways to help shape the direction and implementation.

## License

*To be determined*

## Contact

For questions or suggestions, please open an issue on GitHub.
