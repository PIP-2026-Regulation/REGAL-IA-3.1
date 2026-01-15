"""Document processing and embedding services for EU AI Act compliance."""

import os
import re
import pickle
import hashlib
import logging
from typing import List, Dict, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a chunk of text from a document with metadata."""
    
    def __init__(self, text: str, page_number: int, chunk_index: int, document_name: str):
        self.text = text
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.document_name = document_name
        self.embedding: Optional[np.ndarray] = None
        self.text_hash = hashlib.md5(text.encode()).hexdigest()
        self.extracted_articles = self._extract_articles()

    def _extract_articles(self) -> List[str]:
        """Extract article references from chunk text."""
        articles = []
        patterns = [
            r'Article\s+(\d+[a-zA-Z]*(?:\(\d+\))?)',
            r'Art\.\s*(\d+[a-zA-Z]*)',
            r'article\s+(\d+[a-zA-Z]*(?:\(\d+\))?)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, self.text, re.IGNORECASE)
            articles.extend(matches)
        return list(set(articles))


class DocumentProcessor:
    """Processes PDF documents into chunks for analysis."""
    
    def __init__(self, pdf_path: str, chunk_size: int = 800, overlap: int = 150):
        self.pdf_path = pdf_path
        self.chunk_size = chunk_size
        self.overlap = overlap

    def load_and_chunk_document(self) -> List[DocumentChunk]:
        """Load PDF and split into analyzable chunks."""
        if not os.path.exists(self.pdf_path):
            logger.error(f"PDF not found: {self.pdf_path}")
            return []

        chunks = []
        reader = PdfReader(self.pdf_path)

        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    text = f"[Page {page_num+1}] {text}"
                    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
                    for para in paragraphs:
                        if len(para) > self.chunk_size:
                            words = para.split()
                            for i in range(0, len(words), self.chunk_size - self.overlap):
                                chunk_text = ' '.join(words[i:i + self.chunk_size])
                                if len(chunk_text.strip()) > 100:
                                    chunks.append(DocumentChunk(
                                        chunk_text, page_num, len(chunks), "EU_AI_Act"
                                    ))
                        else:
                            chunks.append(DocumentChunk(para, page_num, len(chunks), "EU_AI_Act"))
            except Exception as e:
                logger.warning(f"Page {page_num} failed: {e}")

        logger.info(f"Created {len(chunks)} chunks")
        return chunks


class EmbeddingService:
    """Handles embedding generation and similarity search."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        logger.info(f"Loaded embedding model: {model_name}")

    def generate_embeddings(
        self, chunks: List[DocumentChunk], cache_file: str
    ) -> List[DocumentChunk]:
        """Generate or load cached embeddings for chunks."""
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached = pickle.load(f)
                if len(cached.get('hashes', [])) == len(chunks):
                    logger.info("Using cached embeddings")
                    for i, chunk in enumerate(chunks):
                        chunk.embedding = cached['embeddings'][i]
                    return chunks
            except Exception as e:
                logger.warning(f"Cache load failed: {e}")

        logger.info("Generating embeddings...")
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'hashes': [c.text_hash for c in chunks],
                    'embeddings': embeddings
                }, f)
            logger.info(f"Embeddings cached to {cache_file}")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

        return chunks

    def find_relevant_chunks(
        self, query: str, chunks: List[DocumentChunk], top_k: int = 7
    ) -> List[DocumentChunk]:
        """Find most relevant chunks for a query using cosine similarity."""
        try:
            query_emb = self.model.encode([query])[0]
            valid = [(c, c.embedding) for c in chunks if c.embedding is not None]
            if not valid:
                return chunks[:top_k]
            
            chunks_list, embeddings = zip(*valid)
            similarities = cosine_similarity([query_emb], embeddings)[0]
            top_idx = np.argsort(similarities)[-top_k:][::-1]
            
            selected_chunks = []
            selected_hashes = set()
            for i in top_idx:
                chunk = chunks_list[i]
                if chunk.text_hash not in selected_hashes:
                    selected_chunks.append(chunk)
                    selected_hashes.add(chunk.text_hash)
                    if len(selected_chunks) >= top_k:
                        break
            return selected_chunks
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return chunks[:top_k]

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts."""
        try:
            emb1 = self.model.encode([text1])[0]
            emb2 = self.model.encode([text2])[0]
            return float(cosine_similarity([emb1], [emb2])[0][0])
        except:
            return 0.0
