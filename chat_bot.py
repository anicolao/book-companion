"""
Chat Bot for Ollama integration.
Provides context-aware responses using local LLM.
"""

import requests
from typing import List


class ChatBot:
    """Handles interaction with Ollama local LLM."""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        """
        Initialize ChatBot.
        
        Args:
            model: Ollama model to use (default: llama2)
            base_url: Ollama API base URL
        """
        self.model = model
        self.base_url = base_url
    
    def ask_companion(self, question: str, book_context: str, book_title: str = "the book") -> str:
        """
        Ask the companion a question with book context.
        
        Args:
            question: User's question
            book_context: Relevant excerpt from the book
            book_title: Title of the book
            
        Returns:
            AI response as string
        """
        prompt = f"""Based on this excerpt from "{book_title}":

{book_context}

Question: {question}

Provide a helpful, concise answer based on the context. Keep your response under 100 words."""
        
        try:
            response = requests.post(
                f'{self.base_url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.RequestException as e:
            raise Exception(f"Failed to get response from Ollama: {e}")
    
    def get_context_window(self, paragraphs: List[str], current_index: int, window_size: int = 5) -> str:
        """
        Get a context window around the current paragraph.
        
        Args:
            paragraphs: List of all paragraphs
            current_index: Index of current paragraph
            window_size: Number of paragraphs before and after to include
            
        Returns:
            Combined context as string
        """
        start = max(0, current_index - window_size)
        end = min(len(paragraphs), current_index + window_size + 1)
        
        context_paragraphs = paragraphs[start:end]
        return '\n\n'.join(context_paragraphs)
    
    def check_ollama_status(self) -> bool:
        """
        Check if Ollama is running and accessible.
        
        Returns:
            True if Ollama is available
        """
        try:
            response = requests.get(f'{self.base_url}/api/tags', timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
