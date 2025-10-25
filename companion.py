"""
Book Companion - Main TUI Application
An interactive audiobook companion using Textual TUI framework.
"""

import json
import threading
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Label
from textual.reactive import reactive

from book_manager import BookManager
from audio_controller import AudioController
from chat_bot import ChatBot


class CompanionApp(App):
    """Book Companion TUI Application."""

    CSS = """
    Screen {
        background: $surface;
    }

    #title-container, #book-info-container {
        height: auto;
        background: $panel;
        padding: 1;
        margin: 1;
    }

    #book-info {
        height: auto;
        color: $text;
    }

    #current-text {
        height: 10;
        background: $surface;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }

    #controls {
        height: auto;
        align: center middle;
        margin: 1;
    }

    #chat-area {
        height: auto;
        background: $panel;
        padding: 1;
        margin: 1;
        min-height: 5;
    }

    #chat-display {
        width: 100%;
        content-align: left top;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("p", "toggle_play", "Play/Pause"),
        ("n", "next_paragraph", "Next"),
        ("b", "previous_paragraph", "Previous"),
        ("w", "toggle_wake_word", "Wake Word"),
        ("q", "quit", "Quit"),
    ]

    # Reactive attributes
    is_playing = reactive(False)
    current_paragraph_index = reactive(0)

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.book_manager = BookManager()
        self.audio_controller = AudioController()
        self.chat_bot = ChatBot()

        self.paragraphs = []
        self.book_title = ""
        self.state_file = Path("data/state.json")

        # Wake word detection
        self._wake_word_enabled = False
        self._wake_word_thread = None

        # Load state
        self.load_state()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        yield Container(
            Label("Book Companion - POC v0.1", id="title"),
            id="title-container"
        )

        yield Container(
            Label(self._get_book_info(), id="book-info"),
            id="book-info-container"
        )

        yield Container(
            Label(self._get_current_text(), id="text-display"),
            id="current-text"
        )

        yield Horizontal(
            Button(
                "▶ Play" if not self.is_playing else "⏸ Pause",
                id="play-btn",
                variant="primary"
            ),
            Button("⏮ Previous", id="prev-btn"),
            Button("⏭ Next", id="next-btn"),
            id="controls"
        )

        yield Container(
            Label("", id="chat-display"),
            id="chat-area"
        )

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Load book if not already loaded
        if not self.paragraphs:
            try:
                self.paragraphs = self.book_manager.download_book(46)
                self.book_title = self.book_manager.get_book_title(46)
                # After loading book, load state to get correct position
                self.load_state()
                self.refresh_display()
            except Exception as e:
                self.show_message(f"Error loading book: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "play-btn":
            self.action_toggle_play()
        elif button_id == "next-btn":
            self.action_next_paragraph()
        elif button_id == "prev-btn":
            self.action_previous_paragraph()

    def action_toggle_play(self) -> None:
        """Toggle play/pause."""
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()

    def action_next_paragraph(self) -> None:
        """Skip to next paragraph."""
        if self.current_paragraph_index < len(self.paragraphs) - 1:
            self.audio_controller.stop_speaking()
            self.current_paragraph_index += 1
            self.save_state()
            self.refresh_display()
            if self.is_playing:
                self.speak_current_paragraph()

    def action_previous_paragraph(self) -> None:
        """Go to previous paragraph."""
        if self.current_paragraph_index > 0:
            self.audio_controller.stop_speaking()
            self.current_paragraph_index -= 1
            self.save_state()
            self.refresh_display()
            if self.is_playing:
                self.speak_current_paragraph()

    def action_toggle_wake_word(self) -> None:
        """Toggle wake word detection on/off."""
        if self._wake_word_enabled:
            self._stop_wake_word_detection()
        else:
            self._start_wake_word_detection()

    def _start_wake_word_detection(self) -> None:
        """Start listening for wake word in background."""
        if self._wake_word_enabled:
            return

        # Test if speech recognition is available
        try:
            import speech_recognition as sr
            # Try to access microphone to test availability
            sr.Recognizer()
            with sr.Microphone():
                pass  # Just test access
        except ImportError:
            self.show_message(
                "ERROR: speech_recognition not installed. "
                "Make sure you're in the Nix environment (nix develop)"
            )
            return
        except Exception as mic_error:
            self.show_message(f"ERROR: Cannot access microphone: {mic_error}")
            return

        self._wake_word_enabled = True
        self.show_message("Wake word detection enabled. Say 'hey companion'...")

        def listen_loop():
            error_count = 0
            while self._wake_word_enabled:
                try:
                    if self.audio_controller.listen_for_wake_word(timeout=2):
                        # Wake word detected!
                        error_count = 0  # Reset error count on success
                        self.call_from_thread(self._handle_wake_word)
                except Exception as listen_error:
                    error_count += 1
                    if error_count <= 2:  # Show first few errors
                        err_msg = str(listen_error)
                        self.call_from_thread(
                            lambda msg=err_msg: self.show_message(f"Wake word error: {msg}")
                        )
                    if error_count > 10:  # Stop after too many errors
                        self._wake_word_enabled = False
                        self.call_from_thread(
                            lambda: self.show_message(
                                "Wake word detection stopped due to errors"
                            )
                        )

        self._wake_word_thread = threading.Thread(target=listen_loop, daemon=True)
        self._wake_word_thread.start()

    def _stop_wake_word_detection(self) -> None:
        """Stop wake word detection."""
        self._wake_word_enabled = False
        self.show_message("Wake word detection disabled")

    def _handle_wake_word(self) -> None:
        """Handle wake word detection."""
        # Pause playback if playing
        was_playing = self.is_playing
        if was_playing:
            self.pause_playback()

        self.show_message("🎤 Wake word detected! Listening...")

        # Get question from user
        try:
            def on_listening():
                """Called when actively listening for speech."""
                # Already in app thread (via call_from_thread),
                # so direct call to show_message
                self.show_message("🎤 Listening... (speak now)")

            question = self.audio_controller.capture_question(
                timeout=10,
                on_listening=on_listening
            )
            if question:
                # Show the question immediately
                self.show_message(f"You asked: {question}\n\n💭 Thinking...")

                # Get context and ask AI
                context = self.chat_bot.get_context_window(
                    self.paragraphs,
                    self.current_paragraph_index,
                    window_size=3
                )

                response = self.chat_bot.ask_companion(
                    question,
                    context,
                    self.book_title
                )

                # Display the full response with wrapping
                self.show_message(
                    f"You asked: {question}\n\n"
                    f"🤖 Companion: {response}"
                )

                # Speak response (blocking so text shows before speech)
                self.audio_controller.speak_as_companion(response, blocking=True)

                # Resume playback if it was playing
                if was_playing:
                    self.start_playback()
            else:
                self.show_message("❌ No question detected")
        except Exception as e:
            self.show_message(f"❌ Error: {e}")

    def start_playback(self) -> None:
        """Start reading the book."""
        self.is_playing = True
        self.update_play_button()
        self.speak_current_paragraph()

    def pause_playback(self) -> None:
        """Pause reading."""
        self.is_playing = False
        self.audio_controller.stop_speaking()
        self.update_play_button()

    def speak_current_paragraph(self) -> None:
        """Speak the current paragraph."""
        if not self.paragraphs or self.current_paragraph_index >= len(self.paragraphs):
            # Reached end of book
            self.is_playing = False
            self.update_play_button()
            self.show_message("Reached end of book")
            return

        text = self.paragraphs[self.current_paragraph_index]
        try:
            # Use callback to continue to next paragraph when done
            self.audio_controller.speak_as_narrator(
                text,
                blocking=False,
                on_complete=self._on_paragraph_complete
            )
        except Exception as e:
            self.show_message(f"Error speaking: {e}")

    def _on_paragraph_complete(self) -> None:
        """Called when a paragraph finishes speaking."""
        if self.is_playing and self.current_paragraph_index < len(self.paragraphs) - 1:
            # Auto-advance to next paragraph
            self.current_paragraph_index += 1
            self.save_state()
            self.call_from_thread(self.refresh_display)
            self.call_from_thread(self.speak_current_paragraph)

    def update_play_button(self) -> None:
        """Update play button label."""
        play_btn = self.query_one("#play-btn", Button)
        play_btn.label = "⏸ Pause" if self.is_playing else "▶ Play"

    def refresh_display(self) -> None:
        """Refresh the display with current information."""
        # Update book info
        book_info = self.query_one("#book-info", Label)
        book_info.update(self._get_book_info())

        # Update current text
        text_display = self.query_one("#text-display", Label)
        text_display.update(self._get_current_text())

    def _get_book_info(self) -> str:
        """Get book information string."""
        if not self.paragraphs:
            return "Loading book..."

        return (
            f"Now reading: {self.book_title}\n"
            f"Position: Paragraph {self.current_paragraph_index + 1} "
            f"of {len(self.paragraphs)}"
        )

    def _get_current_text(self) -> str:
        """Get current paragraph text."""
        if not self.paragraphs or self.current_paragraph_index >= len(self.paragraphs):
            return "No text available"

        text = self.paragraphs[self.current_paragraph_index]
        # Truncate if too long
        max_length = 500
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def show_message(self, message: str) -> None:
        """Show a message in the chat area."""
        chat_display = self.query_one("#chat-display", Label)
        chat_display.update(message)

    def load_state(self) -> None:
        """Load saved state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Only load if we have paragraphs loaded
                    if self.paragraphs:
                        saved_index = state.get('current_paragraph', 0)
                        # Ensure index is valid
                        if 0 <= saved_index < len(self.paragraphs):
                            self.current_paragraph_index = saved_index
            except Exception:
                pass  # Use defaults if state file is corrupted

    def save_state(self) -> None:
        """Save current state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'current_paragraph': self.current_paragraph_index,
                    'book_title': self.book_title
                }, f)
        except Exception:
            pass  # Fail silently for state saving

    def on_unmount(self) -> None:
        """Called when app is unmounted."""
        self._stop_wake_word_detection()
        self.audio_controller.stop_speaking()
        self.save_state()


def main():
    """Main entry point."""
    app = CompanionApp()
    app.run()


if __name__ == "__main__":
    main()
