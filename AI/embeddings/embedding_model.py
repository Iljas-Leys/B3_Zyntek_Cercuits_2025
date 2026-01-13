"""
Embedding Model Module - Agent TSE
SCRUM-148, 149, 150: Generate and store embeddings
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple
import json
from pathlib import Path


class EmbeddingModel:
    """Lightweight embedding model for local inference"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model
        
        Args:
            model_name: Hugging Face model name
                - all-MiniLM-L6-v2: Fast, 384 dimensions (default)
                - BAAI/bge-small-en-v1.5: Good quality, 384 dimensions
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"✓ Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text string
            
        Returns:
            Numpy array of embeddings
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts (efficient batching)
        
        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once
            
        Returns:
            Numpy array of shape (num_texts, embedding_dim)
        """
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings
    
    def embed_chunks_from_file(self, chunks_file: str) -> List[Dict]:
        """
        Generate embeddings for chunks stored in a file
        
        Args:
            chunks_file: Path to file containing text chunks
            
        Returns:
            List of dicts with chunk text and embeddings
        """
        chunks_path = Path(chunks_file)
        
        if not chunks_path.exists():
            raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
        
        # Read chunks (assuming one chunk per line for now)
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = [line.strip() for line in f if line.strip()]
        
        print(f"Processing {len(chunks)} chunks...")
        embeddings = self.generate_embeddings_batch(chunks)
        
        # Combine chunks with their embeddings
        results = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            results.append({
                'chunk_id': f"chunk_{i}",
                'text': chunk,
                'embedding': embedding.tolist(),  # Convert to list for JSON serialization
                'embedding_model': self.model_name
            })
        
        return results


# Test the model
if __name__ == "__main__":
    print("Testing Embedding Model")
    print("=" * 50)
    
    # Initialize
    model = EmbeddingModel()
    
    # Test single embedding
    test_text = "Ceramic PCB substrate with high thermal conductivity"
    embedding = model.generate_embedding(test_text)
    
    print(f"\nTest text: {test_text}")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test batch
    test_texts = [
        "PCB operating temperature 300 degrees",
        "Thermal conductivity 180 W/mK required",
        "Gold metallization on alumina substrate"
    ]
    
    embeddings = model.generate_embeddings_batch(test_texts)
    print(f"\nBatch embeddings shape: {embeddings.shape}")
    print("✓ Model working correctly!")