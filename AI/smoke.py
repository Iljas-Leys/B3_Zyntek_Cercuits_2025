# AI/smoke.py
from __future__ import annotations

import sys
from . import core


def main() -> int:
    print("=== SMOKE TEST ===")

    # Redis connectivity + module check
    r = core.get_redis()
    try:
        pong = r.ping()
        print("[OK] Redis ping:", pong)
        core.ensure_redis_has_search_module(r)
        print("[OK] RediSearch available (Redis Stack)")
    except Exception as e:
        print("[FAIL] Redis/RediSearch:", e)
        return 1

    # Create index (151)
    try:
        core.create_index_from_yaml("redisSchema.yaml", drop_existing=True)
        print("[OK] Index created:", core.REDIS_INDEX_NAME)
        # core.create_index_from_yaml sets these globals based on schema
        print("[OK] Using schema fields:",
              f"text={core._SCHEMA_TEXT_FIELD}",
              f"vector={core._SCHEMA_VECTOR_FIELD}",
              f"prefix={core._SCHEMA_PREFIX}")
    except Exception as e:
        print("[FAIL] Index creation (151):", e)
        return 1

    # Insert dummy chunks + retrieval (153)
    texts = [
        "Redis Stack supports vector search using RediSearch.",
        "Sentence-Transformers generates embeddings locally for data privacy.",
        "Ollama runs local LLM models and supports multiple model choices.",
        "Cosine similarity compares vectors by direction (angle).",
        "RAG retrieves relevant chunks then prompts the LLM with context."
    ]

    try:
        vecs = core.embed_texts(texts)
        print("[OK] Embeddings generated shape:", vecs.shape)
    except Exception as e:
        print("[FAIL] Embedding generation:", e)
        return 1

    try:
        for i, (t, v) in enumerate(zip(texts, vecs)):
            key = core.make_key("test", str(i))
            core.upsert_chunk(r=r, key=key, text=t, embedding=v)
        print("[OK] Inserted dummy chunks")
    except Exception as e:
        print("[FAIL] Insert chunks:", e)
        return 1

    try:
        q = "How do we do vector search in Redis?"
        qv = core.embed_texts([q])[0]
        hits = core.knn_search(r, qv, k=3)
        print("[OK] Retrieval results:")
        for h in hits:
            txt = h.get(core._SCHEMA_TEXT_FIELD, "")
            print(f"  - score={h['score']:.6f} text={txt}")
    except Exception as e:
        print("[FAIL] Retrieval query (153):", e)
        return 1

    # Ollama model check + generate (154)
    try:
        models = core.ollama_list_models()
        print("[OK] Ollama models:", models)
        if core.OLLAMA_MODEL not in models:
            print(f"[WARN] Selected OLLAMA_MODEL '{core.OLLAMA_MODEL}' not found.")
            print("       Pull one: ollama pull llama3   (or mistral / gemma)")
        else:
            out = core.ollama_generate("Say 'OK' and explain what RAG is in one sentence.")
            print("[OK] Ollama generate sample:\n", out)
    except Exception as e:
        print("[FAIL] Ollama list/generate (154):", e)
        return 1

    # RAG (163) - retrieve then prompt LLM
    try:
        question = "What is Redis used for in this system?"
        qv = core.embed_texts([question])[0]
        chunks = core.knn_search(r, qv, k=4)
        prompt = core.build_rag_prompt(question, chunks)
        answer = core.ollama_generate(prompt)
        print("[OK] RAG answer (163):\n", answer)
    except Exception as e:
        print("[FAIL] RAG run (163):", e)
        return 1

    print("=== ALL DONE ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
