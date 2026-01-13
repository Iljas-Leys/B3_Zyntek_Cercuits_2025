# AI/core.py
from __future__ import annotations

"""Core utilities for the minimal RAG system.

This module is intentionally the "one stop" for:
  - Redis Stack checks + RediSearch index creation from redisSchema.yaml
  - Local embedding generation (Sentence-Transformers)
  - Vector similarity search (KNN)
  - A grounded RAG prompt + Ollama generation

It is used by:
  - AI/smoke.py (smoke test)
  - AI/index_storage.py (indexing extracted storage docs)
  - AI/retrieval_real.py (CLI query)
  - AI/benchmarks/* (baseline + eval + compare)
"""

import os
import re
from typing import Any

import yaml
import requests
import numpy as np
import redis

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# -----------------------
# Config / Env
# -----------------------
load_dotenv()

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_INDEX_NAME = os.getenv("REDIS_INDEX_NAME", "rag-index")
REDIS_KEY_PREFIX = os.getenv("REDIS_KEY_PREFIX", "doc")  # expected schema prefix

# Embeddings (Sentence-Transformers)
EMBED_MODEL_NAME = os.getenv(
    "EMBED_MODEL_NAME",
    os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
)
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))
VECTOR_DISTANCE = os.getenv("VECTOR_DISTANCE", "cosine")  # cosine / l2 / ip

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "256"))

# Retrieval quality gates (very cheap and effective)
RAG_MIN_CHARS = int(os.getenv("RAG_MIN_CHARS", "220"))
RAG_FETCH_MULT = int(os.getenv("RAG_FETCH_MULT", "10"))
RAG_MAX_PER_DOC = int(os.getenv("RAG_MAX_PER_DOC", "2"))
RAG_MAX_DISTANCE = float(os.getenv("RAG_MAX_DISTANCE", "0.80"))

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "our", "that", "the", "their", "them",
    "then", "there", "these", "they", "this", "to", "up", "was", "we", "were", "what",
    "when", "where", "which", "who", "with", "you", "your",
}


# -----------------------
# Schema-derived globals (populated by create_index_from_yaml / ensure_index)
# -----------------------
_SCHEMA_TEXT_FIELD = "content"
_SCHEMA_VECTOR_FIELD = "content_embedding"
_SCHEMA_PREFIX = REDIS_KEY_PREFIX or "doc"


# -----------------------
# Redis
# -----------------------
def get_redis() -> redis.Redis:
    # decode_responses=False keeps embeddings as bytes safely
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD or None,
        decode_responses=False,
    )


def ensure_redis_has_search_module(r: redis.Redis) -> None:
    """Fail fast if the server is plain Redis (no RediSearch).

    Redis Stack includes RediSearch, plain redis does not.
    """
    try:
        r.execute_command("FT._LIST")
    except Exception as e:
        raise RuntimeError(
            "RediSearch module not available. You MUST use Redis Stack.\n"
            "Docker example:\n"
            "  docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest"
        ) from e


def _load_schema(schema_path: str) -> dict:
    """Load schema yaml and also populate schema globals."""
    global _SCHEMA_TEXT_FIELD, _SCHEMA_VECTOR_FIELD, _SCHEMA_PREFIX

    with open(schema_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    index_cfg = cfg.get("index", {}) or {}
    idx_name = str(index_cfg.get("name") or "").strip()
    if idx_name and idx_name != REDIS_INDEX_NAME:
        raise RuntimeError(f"Schema index '{idx_name}' != env REDIS_INDEX_NAME '{REDIS_INDEX_NAME}'")

    _SCHEMA_PREFIX = str(index_cfg.get("prefix") or REDIS_KEY_PREFIX or "doc").strip() or "doc"

    fields_list = cfg.get("fields")
    if not isinstance(fields_list, list):
        raise RuntimeError("redisSchema.yaml 'fields' must be a list")

    text_fields: list[str] = []
    vector_field_def: dict | None = None

    for fdef in fields_list:
        ftype = str(fdef.get("type", "")).lower().strip()
        fname = str(fdef.get("name", "")).strip()
        if not fname:
            continue
        if ftype == "text":
            text_fields.append(fname)
        elif ftype == "vector":
            vector_field_def = fdef

    if not text_fields:
        raise RuntimeError("No TEXT field found in schema")
    if not vector_field_def:
        raise RuntimeError("No VECTOR field found in schema")

    _SCHEMA_TEXT_FIELD = text_fields[0]
    _SCHEMA_VECTOR_FIELD = str(vector_field_def.get("name") or "content_embedding")

    return cfg


def ensure_index(schema_path: str) -> None:
    """Create index if missing (non-destructive)."""
    cfg = _load_schema(schema_path)
    r = get_redis()
    ensure_redis_has_search_module(r)

    try:
        r.execute_command("FT.INFO", REDIS_INDEX_NAME)
        return
    except Exception:
        create_index_from_yaml(schema_path, drop_existing=False, _cfg=cfg)


def create_index_from_yaml(
    schema_path: str,
    drop_existing: bool = True,
    *,
    _cfg: dict | None = None,
) -> None:
    """Create RediSearch index from redisSchema.yaml.

    Supports the schema format used in this repo:
      - index: {name, prefix}
      - fields: [ {name, type, attrs?}, ... ]
        - vector field uses attrs: {algorithm, dims, distance_metric, datatype}
    """
    cfg = _cfg or _load_schema(schema_path)
    r = get_redis()
    ensure_redis_has_search_module(r)

    index_cfg = cfg.get("index", {}) or {}
    idx = str(index_cfg.get("name") or REDIS_INDEX_NAME)
    prefix = str(index_cfg.get("prefix") or _SCHEMA_PREFIX)
    if not prefix:
        raise RuntimeError("redisSchema.yaml missing index.prefix")

    # RediSearch PREFIX should match actual key prefix (keys look like: doc:<doc_id>:<chunk_id>)
    prefix_token = prefix if prefix.endswith(":") else (prefix + ":")

    fields_list = cfg.get("fields") or []

    # Find vector field attrs (dims, distance, dtype)
    vector_field_def = None
    for fdef in fields_list:
        if str(fdef.get("type", "")).lower().strip() == "vector":
            vector_field_def = fdef
            break
    if not vector_field_def:
        raise RuntimeError("No vector field (type: vector) found in schema")

    attrs = vector_field_def.get("attrs", {}) or {}
    algo = str(attrs.get("algorithm", "flat")).upper()
    dims = int(attrs.get("dims", attrs.get("dim", EMBED_DIM)))
    dist = str(attrs.get("distance_metric", VECTOR_DISTANCE)).upper()
    dtype = str(attrs.get("datatype", "float32")).upper()

    # Normalize dtype
    if dtype in ("FLOAT32", "F32", "FLOAT"):
        dtype = "FLOAT32"
    elif dtype in ("FLOAT64", "F64", "DOUBLE"):
        dtype = "FLOAT64"
    else:
        dtype = "FLOAT32"

    if dims != EMBED_DIM:
        raise RuntimeError(f"Schema dims {dims} != env EMBED_DIM {EMBED_DIM}")

    if drop_existing:
        try:
            r.execute_command("FT.DROPINDEX", idx, "DD")
        except Exception:
            pass

    schema_tokens: list[str] = []

    for fdef in fields_list:
        fname = str(fdef.get("name", "")).strip()
        ftype = str(fdef.get("type", "")).lower().strip()
        if not fname or not ftype:
            continue

        if ftype == "text":
            schema_tokens += [fname, "TEXT"]

        elif ftype == "tag":
            sep = ","
            a = fdef.get("attrs", {}) or {}
            if "separator" in a:
                sep = str(a.get("separator") or ",")
            schema_tokens += [fname, "TAG", "SEPARATOR", sep]

        elif ftype == "numeric":
            schema_tokens += [fname, "NUMERIC"]

        elif ftype == "vector":
            vec_args = [
                "TYPE", dtype,
                "DIM", str(dims),
                "DISTANCE_METRIC", dist,
            ]
            schema_tokens += [fname, "VECTOR", algo, str(len(vec_args)), *vec_args]

    cmd = [
        "FT.CREATE", idx,
        "ON", "HASH",
        "PREFIX", "1", prefix_token,
        "SCHEMA",
        *schema_tokens,
    ]
    r.execute_command(*cmd)


def redis_index_doc_count(r: redis.Redis, index_name: str) -> int:
    """Return number of docs indexed by RediSearch."""
    try:
        info = r.execute_command("FT.INFO", index_name)
    except Exception:
        return 0

    # FT.INFO returns a flat list: [k1, v1, k2, v2, ...]
    def _dec(x: Any) -> str:
        if isinstance(x, (bytes, bytearray)):
            return x.decode("utf-8", "ignore")
        return str(x)

    for i in range(0, len(info) - 1, 2):
        k = _dec(info[i]).lower()
        if k == "num_docs":
            v = info[i + 1]
            try:
                return int(_dec(v))
            except Exception:
                return 0
    return 0


# -----------------------
# Key / upsert
# -----------------------
def make_key(doc_id: str, chunk_id: str | int) -> str:
    # ensures keys match schema prefix (e.g. "doc")
    return f"{_SCHEMA_PREFIX}:{doc_id}:{chunk_id}"


def _vec_to_bytes(v: np.ndarray) -> bytes:
    return np.asarray(v, dtype=np.float32).tobytes()


def upsert_chunk(
    *,
    r: redis.Redis,
    key: str,
    text: str,
    embedding: np.ndarray,
    metadata: dict | None = None,
) -> None:
    """Upsert a chunk into Redis.

    `metadata` is optional to keep older scripts working, but for best retrieval quality
    (diversity + source attribution) you should store doc_id/source/title/etc.
    """
    meta = metadata or {}
    payload: dict[bytes, bytes] = {}
    payload[_SCHEMA_TEXT_FIELD.encode()] = (text or "").encode("utf-8", "ignore")
    payload[_SCHEMA_VECTOR_FIELD.encode()] = _vec_to_bytes(embedding)

    for k, v in meta.items():
        if v is None:
            continue
        payload[str(k).encode()] = str(v).encode("utf-8", "ignore")

    r.hset(key, mapping=payload)


# -----------------------
# Embeddings
# -----------------------
_embedder: SentenceTransformer | None = None


def embed_texts(texts: list[str]) -> np.ndarray:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    vecs = _embedder.encode(texts, normalize_embeddings=True)
    vecs = np.asarray(vecs, dtype=np.float32)
    if vecs.ndim != 2 or vecs.shape[1] != EMBED_DIM:
        raise RuntimeError(f"Embedding dim mismatch: got {vecs.shape}, expected (*, {EMBED_DIM})")
    return vecs


# -----------------------
# Vector search
# -----------------------
def knn_search(r: redis.Redis, query_vec: np.ndarray, k: int = 6) -> list[dict]:
    """Return KNN hits from Redis.

    NOTE: with COSINE metric, returned `score` is a *distance* (lower is better).
    """
    q = f"(*)=>[KNN {k} @{_SCHEMA_VECTOR_FIELD} $vec AS score]"
    res = r.execute_command(
        "FT.SEARCH",
        REDIS_INDEX_NAME,
        q,
        "PARAMS",
        "2",
        "vec",
        _vec_to_bytes(query_vec),
        "SORTBY",
        "score",
        "ASC",
        "RETURN",
        "9",
        "score",
        _SCHEMA_TEXT_FIELD,
        "source",
        "title",
        "doc_id",
        "chunk_id",
        "file_type",
        "start_char",
        "end_char",
        "DIALECT",
        "2",
    )

    if not res or len(res) < 2:
        return []

    out: list[dict] = []

    def _dec(x: Any) -> str:
        if isinstance(x, (bytes, bytearray)):
            return x.decode("utf-8", "ignore")
        return str(x)

    for i in range(1, len(res), 2):
        key = res[i]
        fields = res[i + 1]
        row: dict[str, Any] = {"key": _dec(key)}

        for j in range(0, len(fields), 2):
            fk = _dec(fields[j])
            fv = fields[j + 1]

            if fk == "score":
                try:
                    row["score"] = float(_dec(fv))
                except Exception:
                    row["score"] = None
            elif fk == _SCHEMA_TEXT_FIELD:
                row[fk] = _dec(fv)
            else:
                row[fk] = _dec(fv)

        out.append(row)

    return out


# -----------------------
# Retrieval filters + grounding gate
# -----------------------
def _norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def _query_terms(question: str) -> list[str]:
    terms = re.findall(r"[a-zA-Z0-9]+", (question or "").lower())
    return [t for t in terms if t and t not in _STOPWORDS]


def _has_lexical_evidence(question: str, hits: list[dict]) -> bool:
    terms = set(_query_terms(question))
    if not terms:
        return True
    ctx = " ".join(_norm_text(str(h.get(_SCHEMA_TEXT_FIELD, ""))) for h in hits[:5])
    return any(t in ctx for t in terms)


def retrieve_chunks(r: redis.Redis, question: str, k: int = 6) -> list[dict]:
    qv = embed_texts([question])[0]
    k_candidates = max(k * RAG_FETCH_MULT, k)
    raw = knn_search(r, qv, k=k_candidates)

    out: list[dict] = []
    seen_txt: set[str] = set()
    per_doc: dict[str, int] = {}

    for h in raw:
        txt = str(h.get(_SCHEMA_TEXT_FIELD, ""))
        ntxt = _norm_text(txt)
        if len(ntxt) < RAG_MIN_CHARS:
            continue

        doc_id = str(h.get("doc_id") or "")
        if doc_id and per_doc.get(doc_id, 0) >= RAG_MAX_PER_DOC:
            continue

        if ntxt in seen_txt:
            continue
        seen_txt.add(ntxt)

        out.append(h)
        if doc_id:
            per_doc[doc_id] = per_doc.get(doc_id, 0) + 1

        if len(out) >= k:
            break

    return out


def should_answer_grounded(question: str, hits: list[dict]) -> bool:
    if not hits:
        return False

    best = hits[0].get("score", None)
    if not isinstance(best, (int, float)):
        return False

    # cosine distance: lower is better
    if float(best) > RAG_MAX_DISTANCE:
        return False

    # require some lexical evidence to avoid random matches
    if not _has_lexical_evidence(question, hits):
        return False

    return True


# -----------------------
# Ollama calls
# -----------------------
def ollama_list_models() -> list[str]:
    r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
    r.raise_for_status()
    data = r.json()
    return [m.get("name") for m in data.get("models", []) if m.get("name")]


def ollama_generate(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": OLLAMA_MAX_TOKENS,
        },
    }
    r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("response", "").strip()


# -----------------------
# RAG prompt + answer
# -----------------------
def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    blocks = []
    for c in chunks:
        src = c.get("source") or c.get("title") or ""
        text = str(c.get(_SCHEMA_TEXT_FIELD, ""))
        if src:
            blocks.append(f"Source: {src}\n{text}")
        else:
            blocks.append(text)

    context = "\n\n---\n\n".join(blocks) if blocks else "NO_CONTEXT"

    return (
        "You are Agent TSE.\n"
        "You MUST answer using ONLY the context below.\n"
        "Do NOT use outside knowledge. Do NOT guess. Do NOT infer missing facts.\n"
        "If the answer is not explicitly stated in the context, respond EXACTLY with: I don't know\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:\n"
    )


def rag_answer(r: redis.Redis, question: str, k: int = 6) -> tuple[str, list[dict]]:
    hits = retrieve_chunks(r, question, k=k)
    if not should_answer_grounded(question, hits):
        return "I don't know", hits

    prompt = build_rag_prompt(question, hits)
    answer = ollama_generate(prompt)

    ans_norm = (answer or "").strip().lower()
    if not ans_norm or ans_norm == "i don't know" or ans_norm.startswith("i don't know\n"):
        return "I don't know", hits

    return answer, hits
