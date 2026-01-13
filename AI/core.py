# AI/core.py
from __future__ import annotations

import os
import re
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

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_INDEX_NAME = os.getenv("REDIS_INDEX_NAME", "rag-index")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "256"))

# Embeddings model used locally (384 dims commonly for MiniLM)
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

# Schema globals (loaded from redisSchema.yaml)
_SCHEMA_TEXT_FIELD = "content"
_SCHEMA_VECTOR_FIELD = "content_embedding"
_SCHEMA_PREFIX = "doc"

# Tunables for scalable retrieval quality
RAG_MIN_CHARS = int(os.getenv("RAG_MIN_CHARS", "220"))
RAG_FETCH_MULT = int(os.getenv("RAG_FETCH_MULT", "10"))  # fetch k*mult then filter down
RAG_MAX_PER_DOC = int(os.getenv("RAG_MAX_PER_DOC", "2"))
RAG_MAX_DISTANCE = float(os.getenv("RAG_MAX_DISTANCE", "0.80"))

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "our", "that", "the", "their", "them",
    "then", "there", "these", "they", "this", "to", "up", "was", "we", "were", "what",
    "when", "where", "which", "who", "with", "you", "your",
}

# -----------------------
# Redis schema / index
# -----------------------
def _load_schema(schema_path: str) -> None:
    """Loads schema settings from redisSchema.yaml into globals."""
    global _SCHEMA_TEXT_FIELD, _SCHEMA_VECTOR_FIELD, _SCHEMA_PREFIX

    with open(schema_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    index_cfg = cfg.get("index", {})
    _SCHEMA_PREFIX = index_cfg.get("prefix") or "doc"

    fields_list = cfg.get("fields")
    if not isinstance(fields_list, list):
        raise RuntimeError("redisSchema.yaml 'fields' must be a list")

    text_fields: list[str] = []
    vector_field_name: str | None = None
    for fdef in fields_list:
        name = fdef.get("name")
        ftype = (fdef.get("type") or "").upper()
        if not name:
            continue
        if ftype == "TEXT":
            text_fields.append(name)
        if ftype == "VECTOR":
            vector_field_name = name

    if not text_fields:
        raise RuntimeError("Schema must contain at least one TEXT field")
    if not vector_field_name:
        raise RuntimeError("Schema must contain a VECTOR field")

    _SCHEMA_TEXT_FIELD = text_fields[0]
    _SCHEMA_VECTOR_FIELD = vector_field_name


def get_redis() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD or None,
        decode_responses=False,
    )


def ensure_index(schema_path: str) -> None:
    """Create index if missing (non-destructive)."""
    _load_schema(schema_path)
    r = get_redis()
    try:
        r.execute_command("FT.INFO", REDIS_INDEX_NAME)
        return
    except Exception:
        create_index_from_yaml(schema_path, drop_existing=False)


def create_index_from_yaml(schema_path: str, drop_existing: bool = False) -> None:
    """Create RediSearch index from redisSchema.yaml. Optionally drop existing."""
    _load_schema(schema_path)
    r = get_redis()

    if drop_existing:
        try:
            r.execute_command("FT.DROPINDEX", REDIS_INDEX_NAME, "DD")
        except Exception:
            pass

    with open(schema_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    index_cfg = cfg.get("index", {})
    prefix = index_cfg.get("prefix", _SCHEMA_PREFIX)
    dim = int(index_cfg.get("dim", 384))
    distance = index_cfg.get("distance", "COSINE")

    fields_list = cfg.get("fields", [])
    schema_args: list[str] = []
    for fdef in fields_list:
        name = fdef.get("name")
        ftype = (fdef.get("type") or "").upper()
        if not name or not ftype:
            continue

        if ftype == "TEXT":
            schema_args += [name, "TEXT"]
        elif ftype == "TAG":
            schema_args += [name, "TAG", "SEPARATOR", ","]
        elif ftype == "NUMERIC":
            schema_args += [name, "NUMERIC"]
        elif ftype == "VECTOR":
            algorithm = (fdef.get("algorithm") or "FLAT").upper()
            schema_args += [
                name,
                "VECTOR",
                algorithm,
                "6",
                "TYPE",
                "FLOAT32",
                "DIM",
                str(dim),
                "DISTANCE_METRIC",
                distance,
            ]

    r.execute_command(
        "FT.CREATE",
        REDIS_INDEX_NAME,
        "ON",
        "HASH",
        "PREFIX",
        "1",
        f"{prefix}:",
        "SCHEMA",
        *schema_args,
    )


# -----------------------
# Key / upsert
# -----------------------
def make_key(doc_id: str, chunk_id: int) -> str:
    return f"{_SCHEMA_PREFIX}:{doc_id}:{chunk_id}"


def upsert_chunk(
    *,
    r: redis.Redis,
    key: str,
    text: str,
    embedding: np.ndarray,
    metadata: dict,
) -> None:
    payload: dict[bytes, bytes] = {}
    payload[_SCHEMA_TEXT_FIELD.encode()] = (text or "").encode("utf-8", "ignore")
    payload[_SCHEMA_VECTOR_FIELD.encode()] = np.asarray(embedding, dtype=np.float32).tobytes()

    for k, v in metadata.items():
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
        _embedder = SentenceTransformer(EMBED_MODEL)
    vecs = _embedder.encode(texts, normalize_embeddings=True)
    return np.asarray(vecs, dtype=np.float32)


# -----------------------
# Vector search (FIXED: always returns score)
# -----------------------
def knn_search(r: redis.Redis, query_vec: np.ndarray, k: int = 6) -> list[dict]:
    """
    Returns KNN hits from Redis.
    IMPORTANT: with COSINE, the returned 'score' is a distance (lower is better).
    """
    q = f"*=>[KNN {k} @{_SCHEMA_VECTOR_FIELD} $vec AS score]"
    res = r.execute_command(
        "FT.SEARCH",
        REDIS_INDEX_NAME,
        q,
        "PARAMS",
        2,
        "vec",
        np.asarray(query_vec, dtype=np.float32).tobytes(),
        # ✅ RETURN includes score so we always have it in the hit dict
        "RETURN",
        9,
        "score",
        _SCHEMA_TEXT_FIELD,
        "source",
        "title",
        "doc_id",
        "chunk_id",
        "file_type",
        "start_char",
        "end_char",
        "SORTBY",
        "score",
        "ASC",
        "DIALECT",
        2,
    )

    hits: list[dict] = []
    if not res or len(res) < 2:
        return hits

    for i in range(1, len(res), 2):
        key = res[i]
        fields = res[i + 1]
        d: dict = {
            "key": key.decode("utf-8", "ignore") if isinstance(key, (bytes, bytearray)) else str(key)
        }

        for j in range(0, len(fields), 2):
            fk = fields[j]
            fv = fields[j + 1]
            fk = fk.decode("utf-8", "ignore") if isinstance(fk, (bytes, bytearray)) else str(fk)

            if fk == "score":
                fv = fv.decode("utf-8", "ignore") if isinstance(fv, (bytes, bytearray)) else str(fv)
                try:
                    d["score"] = float(fv)
                except Exception:
                    d["score"] = None
            else:
                d[fk] = fv.decode("utf-8", "ignore") if isinstance(fv, (bytes, bytearray)) else str(fv)

        hits.append(d)

    return hits


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


def retrieve_chunks(
    r: redis.Redis,
    question: str,
    k: int = 6,
) -> list[dict]:
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
        # If score missing/invalid, be safe and refuse
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
        "If the answer is not explicitly stated in the context, respond EXACTLY with: I don't know\n"
        "After your answer, add one line: Sources: <comma-separated Source values you used>\n\n"
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
    if not ans_norm:
        return "I don't know", hits
    if ans_norm == "i don't know" or ans_norm.startswith("i don't know\n"):
        return "I don't know", hits

    return answer, hits
