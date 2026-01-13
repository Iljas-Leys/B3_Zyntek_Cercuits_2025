"""AI/chunking.py

SCRUM-142 / SCRUM-135

Chunking with metadata.

We implement two strategies:
1) Semantic chunking (topic-shift boundaries using embedding similarity)
2) Recursive chunking fallback (separator-based, similar to LangChain's RecursiveCharacterTextSplitter)

The public entrypoint is `chunk_document(...)`.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, asdict
from typing import Iterable, List, Literal, Optional

import numpy as np

from . import core


ChunkStrategy = Literal["auto", "semantic", "recursive", "both"]


@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    text: str
    start_char: int
    end_char: int
    source: str = ""
    title: str = ""
    file_type: str = ""

    def metadata(self) -> dict:
        d = asdict(self)
        # text is stored separately as `content`; avoid duplicating
        d.pop("text", None)
        return d


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _split_into_sentences(text: str) -> List[tuple[str, int, int]]:
    """Very small sentence splitter that also keeps char spans."""
    # Keep original text to preserve char indices
    t = text or ""
    if not t.strip():
        return []

    # Split on sentence end punct. This is intentionally simple + dependency-free.
    parts = []
    start = 0
    for m in re.finditer(r"[.!?]+\s+", t):
        end = m.end()
        s = t[start:end].strip()
        if s:
            parts.append((s, start, end))
        start = end
    tail = t[start:].strip()
    if tail:
        parts.append((tail, start, len(t)))
    return parts


def recursive_chunk(
    text: str,
    max_chars: int = 900,
    overlap: int = 150,
    separators: Optional[List[str]] = None,
) -> List[tuple[str, int, int]]:
    """Recursive char chunking with best-effort boundary splits."""
    t = text or ""
    if not t.strip():
        return []

    seps = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_with_sep(span: tuple[int, int], sep_idx: int) -> List[tuple[int, int]]:
        (a, b) = span
        if b - a <= max_chars:
            return [span]
        sep = seps[sep_idx]
        if sep == "":
            # hard split
            out = []
            i = a
            while i < b:
                j = min(b, i + max_chars)
                out.append((i, j))
                i = max(i + 1, j - overlap)
            return out

        # try to split on separator occurrences
        out: List[tuple[int, int]] = []
        i = a
        while i < b:
            j = min(b, i + max_chars)
            cut = t.rfind(sep, i, j)
            if cut == -1 or cut < i + int(max_chars * 0.5):
                # couldn't find good boundary; fall back deeper
                if sep_idx + 1 < len(seps):
                    return split_with_sep(span, sep_idx + 1)
                cut = j
            else:
                cut = cut + len(sep)
            out.append((i, cut))
            i = max(i + 1, cut - overlap)
        return out

    spans = split_with_sep((0, len(t)), 0)
    chunks: List[tuple[str, int, int]] = []
    for a, b in spans:
        s = _normalize_ws(t[a:b])
        if s:
            chunks.append((s, a, b))
    return chunks


def semantic_chunk(
    text: str,
    max_chars: int = 900,
    overlap_chars: int = 150,
    min_chars: int = 250,
    similarity_threshold: float = 0.73,
) -> List[tuple[str, int, int]]:
    """Semantic chunking using embedding similarity between adjacent sentences.

    Assumes embeddings from core.embed_texts are normalized.
    """
    t = text or ""
    if not t.strip():
        return []

    sentences = _split_into_sentences(t)
    if len(sentences) <= 2:
        return recursive_chunk(t, max_chars=max_chars, overlap=overlap_chars)

    sent_texts = [_normalize_ws(s) for (s, _, __) in sentences]
    # If the text is messy and normalizes to empties, fall back
    if not any(sent_texts):
        return recursive_chunk(t, max_chars=max_chars, overlap=overlap_chars)

    vecs = core.embed_texts(sent_texts)
    # cosine similarity is dot product because embeddings are normalized
    sims = (vecs[:-1] * vecs[1:]).sum(axis=1)

    chunks: List[tuple[str, int, int]] = []
    cur_start_i = 0
    cur_start_char = sentences[0][1]

    def flush(end_i_inclusive: int):
        nonlocal cur_start_i, cur_start_char
        start_char = cur_start_char
        end_char = sentences[end_i_inclusive][2]
        raw = t[start_char:end_char]
        s = _normalize_ws(raw)
        if s:
            chunks.append((s, start_char, end_char))
        cur_start_i = end_i_inclusive + 1
        if cur_start_i < len(sentences):
            cur_start_char = sentences[cur_start_i][1]

    # walk similarities and cut when topic shifts, but keep chunk sizes reasonable
    for i, sim in enumerate(sims):
        # current chunk length if we include sentence i
        cur_end_char = sentences[i][2]
        cur_len = cur_end_char - cur_start_char

        # If chunk grows too big, cut regardless
        if cur_len >= max_chars:
            flush(i)
            continue

        # topic shift: similarity dips
        if sim < similarity_threshold and cur_len >= min_chars:
            flush(i)

    # tail
    if cur_start_i < len(sentences):
        flush(len(sentences) - 1)

    # Add overlap by duplicating some tail chars of previous chunk into next
    if overlap_chars > 0 and len(chunks) > 1:
        overlapped: List[tuple[str, int, int]] = []
        for idx, (txt, a, b) in enumerate(chunks):
            if idx == 0:
                overlapped.append((txt, a, b))
                continue
            prev_a, prev_b = chunks[idx - 1][1], chunks[idx - 1][2]
            oa = max(prev_a, prev_b - overlap_chars)
            prefix = _normalize_ws(t[oa:prev_b])
            merged = _normalize_ws(prefix + " " + txt)
            overlapped.append((merged, oa, b))
        chunks = overlapped

    # If semantic chunking produced extremely tiny pieces, fall back
    if len(chunks) > 0 and np.median([len(c[0]) for c in chunks]) < 120:
        return recursive_chunk(t, max_chars=max_chars, overlap=overlap_chars)

    return chunks


def chunk_document(
    *,
    doc_id: str,
    text: str,
    source: str = "",
    title: str = "",
    file_type: str = "",
    strategy: ChunkStrategy = "auto",
    max_chars: int = 900,
    overlap: int = 150,
) -> List[Chunk]:
    """Chunk a document and attach metadata.

    strategy:
      - auto: semantic first, fallback to recursive
      - semantic: semantic only
      - recursive: recursive only
      - both: semantic, and any oversize semantic chunk gets recursively split
    """
    t = text or ""
    if not t.strip():
        return []

    spans: List[tuple[str, int, int]]
    if strategy in ("semantic", "auto", "both"):
        try:
            spans = semantic_chunk(t, max_chars=max_chars, overlap_chars=overlap)
        except Exception:
            spans = []
        if strategy == "semantic":
            pass
        elif strategy in ("auto", "both") and not spans:
            spans = recursive_chunk(t, max_chars=max_chars, overlap=overlap)
    else:
        spans = recursive_chunk(t, max_chars=max_chars, overlap=overlap)

    if strategy == "both":
        refined: List[tuple[str, int, int]] = []
        for txt, a, b in spans:
            if len(txt) <= max_chars:
                refined.append((txt, a, b))
            else:
                refined.extend(recursive_chunk(t[a:b], max_chars=max_chars, overlap=overlap))
        spans = refined

    chunks: List[Chunk] = []
    for idx, (txt, a, b) in enumerate(spans):
        chunk_id = str(idx)
        chunks.append(
            Chunk(
                doc_id=doc_id,
                chunk_id=chunk_id,
                text=txt,
                start_char=a,
                end_char=b,
                source=source,
                title=title,
                file_type=file_type,
            )
        )

    return chunks


def stable_doc_id_from_bytes(filename: str, content: bytes, prefix: str = "doc") -> str:
    """Create a stable ID for a file (same bytes => same id)."""
    stem = re.sub(r"[^a-zA-Z0-9_-]", "_", (filename or "doc"))
    stem = stem[:40].strip("_") or "doc"
    h = hashlib.sha256(content).hexdigest()[:12]
    return f"{prefix}_{stem}_{h}"
