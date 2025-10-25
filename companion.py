"""
Book Companion - Main TUI Application
An interactive audiobook companion using Textual TUI framework.
"""

import json
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

    #status-container {
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

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("p", "toggle_play", "Play/Pause"),
        ("n", "next_paragraph", "Next"),
        ("b", "previous_paragraph", "Previous"),
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

        # Load state
        self.load_state()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        yield Container(
            Label("Book Companion - POC v0.1", id="title"),
            id="status-container"
        )

        yield Container(
            Label(self._get_book_info(), id="book-info"),
            id="status-container"
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
            return

        text = self.paragraphs[self.current_paragraph_index]
        try:
            self.audio_controller.speak_as_narrator(text, blocking=False)
        except Exception as e:
            self.show_message(f"Error speaking: {e}")

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
                    self.current_paragraph_index = state.get('current_paragraph', 0)
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
        self.audio_controller.stop_speaking()
        self.save_state()


def main():
    """Main entry point."""
    app = CompanionApp()
    app.run()


if __name__ == "__main__":
    main()
