"""
Simple developer test for document ingestion
Usage:
    python test_ingestion.py path/to/file.pdf
"""

import sys
from ingestion import DocumentIngestionService

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_ingestion.py <file_path>")
        return

    file_path = sys.argv[1]
    service = DocumentIngestionService()

    print(f"\nTesting file: {file_path}")

    is_valid, message = service.validate_file(file_path)
    print("Validation:", message)

    if not is_valid:
        return

    result = service.ingest(file_path, uploader="test@cercuits.com")

    print("\nIngestion successful")
    print("Document ID:", result.document_id)
    print("File type:", result.metadata.file_type)
    print("Word count:", result.metadata.word_count)
    print("Preview:", result.text[:200], "...\n")

if __name__ == "__main__":
    main()
