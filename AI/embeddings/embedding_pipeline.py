"""
Complete Embedding Pipeline - Agent TSE
SCRUM-148, 149, 150: Chunk -> Embed -> Store in Redis
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.schema import IndexSchema
import redis

from embedding_model import EmbeddingModel
from chunker import TextChunker


class EmbeddingPipeline:
    """Complete pipeline: Chunk text -> Generate embeddings -> Store in Redis"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        """
        Initialize pipeline
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
        """
        print("Initializing Embedding Pipeline...")
        
        # Initialize components
        self.embedding_model = EmbeddingModel()
        self.chunker = TextChunker(chunk_size=512, overlap=50)
        
        # Connect to Redis
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
        
        # Test connection
        try:
            self.redis_client.ping()
            print("✓ Connected to Redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
        
        # Create search index using redisvl
        self.index = None
        self._setup_index()
    
    def _setup_index(self):
        """Setup Redis search index for vectors"""
        schema_dict = {
            "index": {
                "name": "chunks_idx",
                "prefix": "chunk:",
                "storage_type": "json"
            },
            "fields": [
                {"name": "chunk_id", "type": "tag"},
                {"name": "document_id", "type": "tag"},
                {"name": "text", "type": "text"},
                {"name": "chunk_number", "type": "numeric"},
                {
                    "name": "embedding",
                    "type": "vector",
                    "attrs": {
                        "dims": 384,
                        "algorithm": "flat",
                        "distance_metric": "cosine"
                    }
                }
            ]
        }
        
        try:
            schema = IndexSchema.from_dict(schema_dict)
            self.index = SearchIndex(schema, redis_client=self.redis_client)
            self.index.create(overwrite=True)
            print("✓ Created search index")
        except Exception as e:
            print(f"✓ Index already exists or created: {e}")
            schema = IndexSchema.from_dict(schema_dict)
            self.index = SearchIndex(schema, redis_client=self.redis_client)
    
    def process_document(self, text_file: str, document_id: str = None) -> List[str]:
        """
        Complete pipeline: Load text -> Chunk -> Embed -> Store
        
        Args:
            text_file: Path to text file from document ingestion
            document_id: Document identifier
            
        Returns:
            List of chunk IDs stored in Redis
        """
        print(f"\nProcessing document: {text_file}")
        
        # Step 1: Chunk the text
        chunks = self.chunker.chunk_from_file(text_file, document_id)
        print(f"  Created {len(chunks)} chunks")
        
        # Step 2: Generate embeddings
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_model.generate_embeddings_batch(chunk_texts)
        print(f"  Generated {len(embeddings)} embeddings")
        
        # Step 3: Store in Redis
        chunk_ids = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = chunk['chunk_id']
            
            # Prepare data for Redis
            data = {
                "chunk_id": chunk_id,
                "document_id": chunk['document_id'],
                "text": chunk['text'],
                "chunk_number": chunk['chunk_number'],
                "start_position": chunk['start_position'],
                "end_position": chunk['end_position'],
                "embedding": embedding.astype(np.float32).tolist()
            }
            
            # Load into index
            self.index.load([data], id_field="chunk_id")
            chunk_ids.append(chunk_id)
        
        print(f"✓ Stored {len(chunk_ids)} chunks in Redis")
        return chunk_ids
    
    def search_similar(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks using vector similarity
        
        Args:
            query_text: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar chunks with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.generate_embedding(query_text)
        
        # Create vector query
        query = VectorQuery(
            vector=query_embedding.astype(np.float32).tolist(),
            vector_field_name="embedding",
            return_fields=["chunk_id", "document_id", "text"],
            num_results=top_k
        )
        
        # Search
        results = self.index.query(query)
        
        # Format results
        similar_chunks = []
        for result in results:
            similar_chunks.append({
                'chunk_id': result.get('chunk_id', ''),
                'document_id': result.get('document_id', ''),
                'text': result.get('text', ''),
                'score': result.get('vector_distance', 0.0)
            })
        
        return similar_chunks


# Test the pipeline
if __name__ == "__main__":
    print("Testing Complete Embedding Pipeline")
    print("=" * 50)
    
    # Create test text file
    test_file = Path("test_document.txt")
    test_content = """
    Ceramic PCB substrates provide superior thermal management for high-power electronics.
    The alumina base material offers excellent dielectric properties and thermal conductivity up to 180 W/mK.
    Gold metallization ensures reliable electrical connections even in harsh environments.
    Operating temperatures can safely exceed 300 degrees Celsius with proper thermal design.
    These substrates are widely used in automotive power electronics, aerospace systems, and industrial applications.
    The manufacturing process involves screen printing, drying, and high-temperature firing.
    Quality control includes visual inspection, electrical testing, and thermal cycling validation.
    """
    
    test_file.write_text(test_content)
    
    try:
        # Initialize pipeline
        pipeline = EmbeddingPipeline()
        
        # Process document
        chunk_ids = pipeline.process_document(str(test_file), document_id="ceramic_pcb_doc")
        
        # Test search
        print("\n" + "=" * 50)
        print("Testing semantic search...")
        query = "thermal management in PCBs"
        results = pipeline.search_similar(query, top_k=3)
        
        print(f"\nQuery: '{query}'")
        print(f"Found {len(results)} similar chunks:")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Chunk: {result['chunk_id']}")
            print(f"   Score: {result['score']}")
            print(f"   Text: {result['text'][:100]}...")
        
        print("\n✓ Pipeline test complete!")
    
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()