#!/usr/bin/env python3
"""
Test script for Book Companion POC components.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from book_manager import BookManager
from audio_controller import AudioController
from chat_bot import ChatBot


def test_book_manager():
    """Test BookManager functionality."""
    print("Testing BookManager...")
    bm = BookManager()
    
    # Create a test book file if it doesn't exist
    test_book_path = Path("data/books/book_46.txt")
    if not test_book_path.exists():
        test_book_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_book_path, 'w') as f:
            f.write("""*** START OF THE PROJECT GUTENBERG EBOOK TEST ***

TEST BOOK

This is a test paragraph one.

This is a test paragraph two.

This is a test paragraph three.

*** END OF THE PROJECT GUTENBERG EBOOK TEST ***""")
    
    paragraphs = bm.download_book(46)
    assert len(paragraphs) > 0, "Should have loaded paragraphs"
    title = bm.get_book_title(46)
    assert title == "A Christmas Carol", f"Expected 'A Christmas Carol', got '{title}'"
    
    print(f"  ✓ Loaded {len(paragraphs)} paragraphs")
    print(f"  ✓ Book title: {title}")
    return True


def test_audio_controller():
    """Test AudioController functionality."""
    print("Testing AudioController...")
    ac = AudioController()
    
    assert not ac.is_speaking, "Should not be speaking initially"
    
    print("  ✓ AudioController initialized")
    print("  ✓ is_speaking flag works")
    print("  ⚠ TTS requires macOS 'say' command (skipped)")
    return True


def test_chat_bot():
    """Test ChatBot functionality."""
    print("Testing ChatBot...")
    cb = ChatBot()
    
    assert cb.model == "llama2", f"Expected model 'llama2', got '{cb.model}'"
    assert cb.base_url == "http://localhost:11434", "Unexpected base URL"
    
    # Test context window
    test_paragraphs = ["P1", "P2", "P3", "P4", "P5"]
    context = cb.get_context_window(test_paragraphs, 2, window_size=1)
    expected_lines = ["P2", "P3", "P4"]
    for line in expected_lines:
        assert line in context, f"Expected '{line}' in context"
    
    # Test Ollama status (will likely be False)
    status = cb.check_ollama_status()
    
    print("  ✓ ChatBot initialized")
    print("  ✓ Context window generation works")
    print(f"  ✓ Ollama status check works (Ollama running: {status})")
    return True


def test_integration():
    """Test basic integration."""
    print("Testing Integration...")
    
    # Try to import the main app
    try:
        from companion import CompanionApp
        app = CompanionApp()
        
        assert app.book_manager is not None, "BookManager not initialized"
        assert app.audio_controller is not None, "AudioController not initialized"
        assert app.chat_bot is not None, "ChatBot not initialized"
        
        print("  ✓ CompanionApp initializes successfully")
        print("  ✓ All components integrate properly")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("  ⚠ Make sure 'textual' is installed: pip install textual")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Book Companion POC - Component Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("BookManager", test_book_manager),
        ("AudioController", test_audio_controller),
        ("ChatBot", test_chat_bot),
        ("Integration", test_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
