"""EU AI Act Compliance Advisor - Source Package."""

from .document_processor import DocumentChunk, DocumentProcessor, EmbeddingService
from .llm_client import OllamaClient
from .legal_advisor import LegalAdvisor

__all__ = [
    'DocumentChunk',
    'DocumentProcessor', 
    'EmbeddingService',
    'OllamaClient',
    'LegalAdvisor'
]
