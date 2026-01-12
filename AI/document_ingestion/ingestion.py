"""
Document Ingestion Module – Sprint 1 MVP
Handles PDF, DOCX, and EML parsing
SCRUM-139 / SCRUM-140 / SCRUM-141
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from dataclasses import dataclass, asdict

from email import policy
from email.parser import BytesParser

import pypdf
from docx import Document as DocxDocument


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class DocumentMetadata:
    document_id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: str
    uploader: Optional[str]
    file_hash: str
    word_count: int
    extraction_status: str
    error_message: Optional[str] = None


@dataclass
class ExtractedContent:
    document_id: str
    text: str
    metadata: DocumentMetadata


# -----------------------------
# Ingestion Service
# -----------------------------

class DocumentIngestionService:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".eml"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.raw_path = self.storage_path / "raw_files"
        self.text_path = self.storage_path / "extracted_text"
        self.meta_path = self.storage_path / "metadata"

        for p in [self.raw_path, self.text_path, self.meta_path]:
            p.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # Public API
    # -----------------------------

    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        path = Path(file_path)

        if not path.exists():
            return False, f"File not found: {path}"

        if path.stat().st_size == 0:
            return False, "File is empty"

        if path.stat().st_size > self.MAX_FILE_SIZE:
            return False, "File exceeds 50MB limit"

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type: {path.suffix}"

        return True, "File is valid"

    def ingest(self, file_path: str, uploader: str = "system") -> ExtractedContent:
        path = Path(file_path)
        ext = path.suffix.lower()

        with open(path, "rb") as f:
            content_bytes = f.read()

        document_id = self._generate_document_id(path.name, content_bytes)

        if ext == ".pdf":
            text = self._parse_pdf(path)
        elif ext == ".docx":
            text = self._parse_docx(path)
        elif ext == ".eml":
            text = self._parse_eml(path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        cleaned_text = re.sub(r"\s+", " ", text).strip()

        metadata = DocumentMetadata(
            document_id=document_id,
            filename=path.name,
            file_type=ext,
            file_size=len(content_bytes),
            upload_timestamp=datetime.utcnow().isoformat(),
            uploader=uploader,
            file_hash=hashlib.sha256(content_bytes).hexdigest(),
            word_count=len(cleaned_text.split()),
            extraction_status="success",
        )

        self._store_raw_file(document_id, ext, content_bytes)
        self._store_text(document_id, cleaned_text)
        self._store_metadata(metadata)

        return ExtractedContent(
            document_id=document_id,
            text=cleaned_text,
            metadata=metadata
        )

    # -----------------------------
    # Parsers
    # -----------------------------

    def _parse_pdf(self, path: Path) -> str:
        reader = pypdf.PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _parse_docx(self, path: Path) -> str:
        doc = DocxDocument(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    def _parse_eml(self, path: Path) -> str:
        with open(path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_content()
            return ""
        else:
            return msg.get_content()

    # -----------------------------
    # Storage helpers
    # -----------------------------

    def _store_raw_file(self, document_id: str, ext: str, content: bytes):
        with open(self.raw_path / f"{document_id}{ext}", "wb") as f:
            f.write(content)

    def _store_text(self, document_id: str, text: str):
        with open(self.text_path / f"{document_id}.txt", "w", encoding="utf-8") as f:
            f.write(text)

    def _store_metadata(self, metadata: DocumentMetadata):
        with open(self.meta_path / f"{metadata.document_id}.json", "w", encoding="utf-8") as f:
            json.dump(asdict(metadata), f, indent=2)

    def _generate_document_id(self, filename: str, content: bytes) -> str:
        base = re.sub(r"[^a-zA-Z0-9_-]", "_", Path(filename).stem)[:30]
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        h = hashlib.sha256(content).hexdigest()[:12]
        return f"{base}_{ts}_{h}"
