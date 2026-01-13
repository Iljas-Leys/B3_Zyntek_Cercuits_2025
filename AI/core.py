# AI/core.py
from __future__ import annotations

import os
import time
import yaml
import requests
import numpy as np
import redis
import psycopg2

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# -----------------------
# Config (from .env)
# -----------------------
load_dotenv()

# Postgres
PG_HOST = os.getenv("PG_HOST", "")
PG_PORT = int(os.getenv("PG_PORT"))
PG_DATABASE = os.getenv("PG_DATABASE", "")
PG_USER = os.getenv("PG_USER", "")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_INDEX_NAME = os.getenv("REDIS_INDEX_NAME", "rag-index")
REDIS_KEY_PREFIX = os.getenv("REDIS_KEY_PREFIX", "doc")  # prefix for keys, matches schema index.prefix

# Embeddings
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))
VECTOR_DISTANCE = os.getenv("VECTOR_DISTANCE", "cosine")  # cosine / l2 / ip

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "250"))


# -----------------------
# Schema-derived globals (populated by create_index_from_yaml)
# -----------------------
_SCHEMA_TEXT_FIELD = "content"
_SCHEMA_VECTOR_FIELD = "content_embedding"
_SCHEMA_PREFIX = "doc"
_SCHEMA_FIELD_NAMES: list[str] = [_SCHEMA_TEXT_FIELD, _SCHEMA_VECTOR_FIELD]


def _b2s(x) -> str:
    """bytes/str -> str"""
    if isinstance(x, (bytes, bytearray)):
        return x.decode("utf-8", errors="replace")
    return str(x)


def _load_schema_fields_from_yaml(schema_path: str = "redisSchema.yaml") -> None:
    """Load schema field names/prefix from redisSchema.yaml without creating/dropping indexes."""
    global _SCHEMA_TEXT_FIELD, _SCHEMA_VECTOR_FIELD, _SCHEMA_PREFIX, _SCHEMA_FIELD_NAMES

    with open(schema_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    index_cfg = cfg.get("index", {})
    prefix = index_cfg.get("prefix")

    fields_list = cfg.get("fields")
    if not isinstance(fields_list, list):
        raise RuntimeError("redisSchema.yaml 'fields' must be a list")

    text_fields: list[str] = []
    vector_field_def = None
    all_fields: list[str] = []
    for fdef in fields_list:
        ftype = str(fdef.get("type", "")).lower()
        fname = str(fdef.get("name", "")).strip()
        if not fname:
            continue
        all_fields.append(fname)
        if ftype == "text":
            text_fields.append(fname)
        elif ftype == "vector":
            vector_field_def = fdef

    if not text_fields:
        raise RuntimeError("No text field found in schema (type: text)")
    if not vector_field_def:
        raise RuntimeError("No vector field found in schema (type: vector)")
    if not prefix:
        raise RuntimeError("redisSchema.yaml missing index.prefix")

    _SCHEMA_TEXT_FIELD = text_fields[0]
    _SCHEMA_VECTOR_FIELD = str(vector_field_def["name"])
    _SCHEMA_PREFIX = str(prefix)
    _SCHEMA_FIELD_NAMES = all_fields



def redis_index_exists(r: redis.Redis, index_name: str) -> bool:
    """Return True if the given RediSearch index exists."""
    try:
        names = r.execute_command("FT._LIST")
        decoded = [_b2s(n) for n in names]
        return index_name in decoded
    except Exception:
        return False


def redis_index_doc_count(r: redis.Redis, index_name: str) -> int:
    """Return number of docs in an index (0 if missing)."""
    try:
        info = r.execute_command("FT.INFO", index_name)
        # info is [k1,v1,k2,v2,...]
        d = {}
        for i in range(0, len(info), 2):
            k = _b2s(info[i])
            v = info[i+1]
            d[k] = v
        num = d.get("num_docs", 0)
        if isinstance(num, (bytes, bytearray)):
            num = num.decode("utf-8")
        return int(num)
    except Exception:
        return 0


def ensure_index(schema_path: str = "redisSchema.yaml") -> None:
    """
    Ensure the RediSearch vector index exists, without destroying data.
    - Loads schema field names (text/vector/prefix) into globals.
    - Creates the index only if it does not exist.
    """
    r = get_redis()
    ensure_redis_has_search_module(r)
    _load_schema_fields_from_yaml(schema_path)

    if redis_index_exists(r, REDIS_INDEX_NAME):
        return

    create_index_from_yaml(schema_path=schema_path, drop_existing=False)



# -----------------------
# PostgreSQL
# -----------------------
def get_postgres_conn():
    if not (PG_HOST and PG_DATABASE and PG_USER):
        raise RuntimeError("Postgres env vars missing. Please set PG_HOST/PG_DATABASE/PG_USER/PG_PASSWORD in .env")

    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5,
    )


def postgres_smoke_test() -> None:
    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            _ = cur.fetchone()
    finally:
        conn.close()


# -----------------------
# Redis
# -----------------------
def get_redis() -> redis.Redis:
    # decode_responses=False keeps embeddings as bytes safely
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)


def ensure_redis_has_search_module(r: redis.Redis) -> None:
    """
    Redis Stack includes RediSearch. Plain redis won't.
    """
    try:
        r.execute_command("FT._LIST")
    except Exception as e:
        raise RuntimeError(
            "RediSearch module not available. You MUST use Redis Stack.\n"
            "Docker: docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest"
        ) from e


def create_index_from_yaml(schema_path: str = "redisSchema.yaml", drop_existing: bool = True) -> None:
  
    global _SCHEMA_TEXT_FIELD, _SCHEMA_VECTOR_FIELD, _SCHEMA_PREFIX, _SCHEMA_FIELD_NAMES

    r = get_redis()
    ensure_redis_has_search_module(r)

    with open(schema_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    index_cfg = cfg.get("index", {})
    idx = index_cfg.get("name")
    prefix = index_cfg.get("prefix")

    if not idx or not prefix:
        raise RuntimeError("redisSchema.yaml missing index.name or index.prefix")

    if idx != REDIS_INDEX_NAME:
        raise RuntimeError(f"Schema index '{idx}' != env REDIS_INDEX_NAME '{REDIS_INDEX_NAME}'")

    fields_list = cfg.get("fields")
    if not isinstance(fields_list, list):
        raise RuntimeError("redisSchema.yaml 'fields' must be a list")

    text_fields: list[str] = []
    vector_field_def = None
    tag_fields: list[dict] = []
    numeric_fields: list[str] = []
    extra_text_fields: list[str] = []
    all_fields: list[str] = []

    for fdef in fields_list:
        ftype = str(fdef.get("type", "")).lower()
        fname = str(fdef.get("name", "")).strip()
        if not fname:
            continue
        all_fields.append(fname)
        if ftype == "text":
            text_fields.append(fname)
        elif ftype == "vector":
            vector_field_def = fdef
        elif ftype == "tag":
            tag_fields.append(fdef)
        elif ftype == "numeric":
            numeric_fields.append(fname)

    if not text_fields:
        raise RuntimeError("No text field found in schema (type: text)")
    if not vector_field_def:
        raise RuntimeError("No vector field found in schema (type: vector)")

    _SCHEMA_TEXT_FIELD = text_fields[0]
    _SCHEMA_VECTOR_FIELD = str(vector_field_def["name"])
    _SCHEMA_PREFIX = str(prefix)
    _SCHEMA_FIELD_NAMES = all_fields

    attrs = vector_field_def.get("attrs", {})
    algo = str(attrs.get("algorithm", "flat")).upper()  # FLAT / HNSW
    dims = int(attrs.get("dims", attrs.get("dim", 0)))
    dist = str(attrs.get("distance_metric", VECTOR_DISTANCE)).upper()
    dtype = str(attrs.get("datatype", "float32")).upper()

    # Normalize dtype
    if dtype in ("FLOAT32", "F32", "FLOAT"):
        dtype = "FLOAT32"
    elif dtype in ("FLOAT64", "F64", "DOUBLE"):
        dtype = "FLOAT64"

    if dims != EMBED_DIM:
        raise RuntimeError(f"Schema dims {dims} != env EMBED_DIM {EMBED_DIM}")

    if drop_existing:
        try:
            r.execute_command("FT.DROPINDEX", idx, "DD")
        except Exception:
            pass

    schema_tokens: list[str] = []

    # Text field(s)
    for tf in text_fields:
        schema_tokens += [tf, "TEXT"]

    # Tag fields (metadata)
    for tf in tag_fields:
        name = str(tf.get("name", "")).strip()
        if not name:
            continue
        # allow custom separator; default works fine for IDs
        sep = str(tf.get("attrs", {}).get("separator", ","))
        schema_tokens += [name, "TAG", "SEPARATOR", sep]

    # Numeric fields (metadata)
    for nf in numeric_fields:
        schema_tokens += [nf, "NUMERIC"]

    # Vector field
    vec_args = [
        "TYPE", dtype,
        "DIM", str(dims),
        "DISTANCE_METRIC", dist,
    ]
    schema_tokens += [
        _SCHEMA_VECTOR_FIELD, "VECTOR", algo, str(len(vec_args)),
        *vec_args
    ]

    cmd = [
        "FT.CREATE", idx,
        "ON", "HASH",
        "PREFIX", "1", prefix,
        "SCHEMA",
        *schema_tokens
    ]

    r.execute_command(*cmd)


def _vec_to_bytes(v: np.ndarray) -> bytes:
    return np.asarray(v, dtype=np.float32).tobytes()


def make_key(doc_id: str, chunk_id: str) -> str:
    # ensures keys match schema prefix (e.g. "doc")
    return f"{_SCHEMA_PREFIX}:{doc_id}:{chunk_id}"


def upsert_chunk(
    r: redis.Redis,
    key: str,
    text: str,
    embedding: np.ndarray,
    metadata: dict | None = None,
) -> None:
    mapping: dict = {
        _SCHEMA_TEXT_FIELD: text,
        _SCHEMA_VECTOR_FIELD: _vec_to_bytes(embedding),
    }
    if metadata:
        # Store metadata fields as-is; RediSearch can index TAG/TEXT/NUMERIC depending on schema.
        for k, v in metadata.items():
            if v is None:
                continue
            if isinstance(v, (dict, list)):
                # keep simple: stringify structured metadata
                mapping[k] = yaml.safe_dump(v, allow_unicode=True)
            else:
                mapping[k] = str(v)

    r.hset(key, mapping=mapping)


def knn_search(
    r: redis.Redis,
    query_vec: np.ndarray,
    k: int = 5,
) -> list[dict]:
    q = f"(*)=>[KNN {k} @{_SCHEMA_VECTOR_FIELD} $vec AS score]"

    # Return content + useful metadata fields (if they exist in schema)
    # Never return the embedding field.
    return_fields: list[str] = []
    for f in _SCHEMA_FIELD_NAMES:
        if f == _SCHEMA_VECTOR_FIELD:
            continue
        # keep responses small by preferring common metadata fields + main text
        if f in (_SCHEMA_TEXT_FIELD, "doc_id", "chunk_id", "source", "filename", "file_type", "title"):
            return_fields.append(f)

    # Always include main content field
    if _SCHEMA_TEXT_FIELD not in return_fields:
        return_fields.insert(0, _SCHEMA_TEXT_FIELD)

    # Include score in RETURN so callers can print/debug ranking.
    return_fields_with_score = list(dict.fromkeys(return_fields + ["score"]))

    res = r.execute_command(
        "FT.SEARCH", REDIS_INDEX_NAME, q,
        "PARAMS", "2", "vec", _vec_to_bytes(query_vec),
        "SORTBY", "score",
        "RETURN", str(len(return_fields_with_score)), *return_fields_with_score,
        "DIALECT", "2",
    )

    out = []
    for i in range(1, len(res), 2):
        key = res[i]
        fields = res[i + 1]
        row = {
            "key": _b2s(key)
        }

        for j in range(0, len(fields), 2):
            f = fields[j]
            v = fields[j + 1]
            fname = _b2s(f)

            if fname == _SCHEMA_TEXT_FIELD and isinstance(v, (bytes, bytearray)):
                v = v.decode("utf-8", errors="replace")
            if fname == "score" and isinstance(v, (bytes, bytearray)):
                v = float(v.decode("utf-8"))
            if isinstance(v, (bytes, bytearray)) and fname != _SCHEMA_VECTOR_FIELD:
                # decode other metadata fields if present
                try:
                    v = v.decode("utf-8", errors="replace")
                except Exception:
                    pass

            row[fname] = v

        out.append(row)

    return out


# -----------------------
# Embeddings (local)
# -----------------------
_embed_model: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


def embed_texts(texts: list[str]) -> np.ndarray:
    m = get_embedder()
    vecs = m.encode(texts, normalize_embeddings=True)
    vecs = np.asarray(vecs, dtype=np.float32)
    if vecs.shape[1] != EMBED_DIM:
        raise RuntimeError(f"Embedding dim mismatch: got {vecs.shape[1]}, expected {EMBED_DIM}")
    return vecs


# -----------------------
# Ollama (multi-model)
# -----------------------
def ollama_list_models() -> list[str]:
    r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
    r.raise_for_status()
    data = r.json()
    return [m["name"] for m in data.get("models", [])]


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
# RAG prompt
# -----------------------
def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    # Keep it simple and strongly grounded
    if not chunks:
        context = "NO_CONTEXT"
    else:
        blocks = []
        for c in chunks:
            src = c.get("source") or c.get("title") or ""
            text = str(c.get(_SCHEMA_TEXT_FIELD, ""))
            if src:
                blocks.append(f"Source: {src}\n{text}")
            else:
                blocks.append(text)
        context = "\n\n---\n\n".join(blocks)

    return (
        "You are Agent TSE.\n"
        "Answer the question using ONLY the context below.\n"
        "If the context does not contain the answer, say \"I don't know\".\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:\n"
    )
