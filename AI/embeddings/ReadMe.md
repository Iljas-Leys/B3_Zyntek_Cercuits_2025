# Embedding Pipeline

## What This Does

Converts text documents into searchable vector embeddings and stores them in Redis.

**Pipeline:** Text → Chunks → Embeddings → Redis Vector DB

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Redis
```bash
docker run -d --name skill-project-redisvl -p 6379:6379 redis:latest
```

### 3. Use the Pipeline
```python
from embedding_pipeline import EmbeddingPipeline

pipeline = EmbeddingPipeline()

# Process a document (output from document_ingestion module)
chunk_ids = pipeline.process_document(
    text_file="path/to/extracted_text.txt",
    document_id="doc_001"
)

# Search for similar content
results = pipeline.search_similar("thermal management PCB", top_k=5)
```

---

## Files

- **`embedding_model.py`** - Loads sentence-transformer model (all-MiniLM-L6-v2, 384 dims)
- **`chunker.py`** - Splits text into 512-token chunks with 50-token overlap
- **`embedding_pipeline.py`** - Complete pipeline: chunk → embed → store → search

---

## Integration with Document Ingestion

After documents are ingested and text is extracted to `/storage/extracted_text/`:
```python
# Document ingestion outputs:
# storage/extracted_text/doc_12345_text.txt

# Embedding pipeline processes it:
pipeline.process_document("storage/extracted_text/doc_12345_text.txt", "doc_12345")
```

**Result:** Document chunks are now searchable in Redis by semantic similarity.

---

## Testing
```bash
python embedding_pipeline.py
```

Should output:
- ✓ Model loaded (384 dimensions)
- ✓ Connected to Redis
- ✓ Stored chunks successfully
- ✓ Search returns similar chunks

---

## Requirements

- Redis running on localhost:6379
- Python 3.11+
- ~90MB model download on first run