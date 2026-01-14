"""
Text Chunking Module - Agent TSE
SCRUM-142: Semantic chunking with overlap
"""

from typing import List, Dict
from pathlib import Path
import json


class TextChunker:
    """Split text into semantic chunks for embedding"""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target tokens per chunk (approximate words)
            overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, document_id: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            document_id: Unique document identifier
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Simple word-based chunking (can be improved with sentence boundaries)
        words = text.split()
        chunks = []
        
        start = 0
        chunk_num = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            chunk_id = f"{document_id}_chunk_{chunk_num}"
            
            chunk_data = {
                'chunk_id': chunk_id,
                'document_id': document_id,
                'text': chunk_text,
                'chunk_number': chunk_num,
                'start_position': start,
                'end_position': min(end, len(words)),
                'metadata': metadata or {}
            }
            
            chunks.append(chunk_data)
            
            # Move forward with overlap
            start = end - self.overlap
            chunk_num += 1
        
        return chunks
    
    def chunk_from_file(self, text_file: str, document_id: str = None) -> List[Dict]:
        """
        Read text file and chunk it
        
        Args:
            text_file: Path to text file
            document_id: Optional document ID (uses filename if not provided)
            
        Returns:
            List of chunks
        """
        text_path = Path(text_file)
        
        if not text_path.exists():
            raise FileNotFoundError(f"Text file not found: {text_file}")
        
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if document_id is None:
            document_id = text_path.stem
        
        return self.chunk_text(text, document_id)


# Test the chunker
if __name__ == "__main__":
    print("Testing Text Chunker")
    print("=" * 50)
    
    chunker = TextChunker(chunk_size=50, overlap=10)
    
    test_text = """
    Ceramic PCB substrates offer superior thermal management for high-power electronics.
    The alumina base provides excellent dielectric properties and thermal conductivity.
    Gold metallization ensures reliable electrical connections in harsh environments.
    Operating temperatures can exceed 300 degrees Celsius with proper design.
    These substrates are commonly used in automotive, aerospace, and industrial applications.
    """
    
    chunks = chunker.chunk_text(test_text, document_id="test_doc_001")
    
    print(f"\nOriginal text length: {len(test_text.split())} words")
    print(f"Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i}:")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  Text: {chunk['text'][:100]}...")
        print(f"  Position: {chunk['start_position']} - {chunk['end_position']}")
    
    print("\n✓ Chunker working correctly!")