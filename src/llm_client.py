"""LLM client for Ollama API interactions."""

import os
import logging
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM API."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1:8b"
    ):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/chat"
        logger.info(f"Initialized Ollama client: {model} @ {base_url}")

    def health_check(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Send chat request to Ollama."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()['message']['content']
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out. Try again.")
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """Stream chat response from Ollama."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        yield data['message']['content']
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}")
        except Exception as e:
            logger.error(f"Stream failed: {e}")
            raise
