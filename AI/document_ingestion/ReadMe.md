# Document Ingestion Module – Sprint 1 MVP

This module ingests customer emails and technical documents for the Cercuits AI Technical Sales Engineer.

It extracts raw text, stores original files, and generates metadata for traceability.

---

## Supported File Types
- `.pdf` – technical documents and drawings
- `.docx` – specifications and reports
- `.eml` – forwarded customer emails

---

## What This Module Does
- Validates uploaded files (type, size, existence)
- Extracts text content
- Stores:
  - raw file
  - extracted text
  - metadata JSON
- Generates a stable `document_id`


## Public API

```python
from ingestion import DocumentIngestionService

service = DocumentIngestionService()

is_valid, message = service.validate_file("example.pdf")

if is_valid:
    result = service.ingest("example.pdf", uploader="engineer@cercuits.com")
    print(result.document_id)
    print(result.metadata.word_count)
