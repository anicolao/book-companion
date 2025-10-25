"""
Book Manager for Project Gutenberg integration.
Downloads, parses, and manages book content.
"""

import requests
from pathlib import Path


class BookManager:
    """Manages downloading and parsing books from Project Gutenberg."""

    def __init__(self, cache_dir="data/books"):
        """
        Initialize BookManager.

        Args:
            cache_dir: Directory to cache downloaded books
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download_book(self, book_id=46):
        """
        Download a book from Project Gutenberg.

        Args:
            book_id: Project Gutenberg book ID (default: 46 - A Christmas Carol)

        Returns:
            List of paragraphs from the book
        """
        cache_file = self.cache_dir / f"book_{book_id}.txt"

        # Check cache first
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            # Download from Project Gutenberg
            url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                text = response.text

                # Cache the download
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(text)
            except requests.RequestException as e:
                raise Exception(f"Failed to download book {book_id}: {e}")

        return self.parse_book(text)

    def parse_book(self, text):
        """
        Parse book text into paragraphs.

        Args:
            text: Raw book text from Project Gutenberg

        Returns:
            List of paragraphs (strings)
        """
        # Remove Gutenberg header/footer
        start_marker = "*** START OF"
        end_marker = "*** END OF"

        start = text.find(start_marker)
        end = text.find(end_marker)

        if start >= 0 and end > start:
            # Find the end of the START line and skip to next line
            start = text.find('\n', start) + 1
            # Skip any empty lines after the marker
            while start < len(text) and text[start] in '\n\r':
                start += 1
            body = text[start:end]
        else:
            body = text

        # Split into paragraphs and filter empty ones
        paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]

        return paragraphs

    def get_book_title(self, book_id=46):
        """
        Get the title of a book.

        Args:
            book_id: Project Gutenberg book ID

        Returns:
            Book title as string
        """
        # Simple mapping for POC
        titles = {
            46: "A Christmas Carol",
            # Add more as needed
        }
        return titles.get(book_id, f"Book #{book_id}")
