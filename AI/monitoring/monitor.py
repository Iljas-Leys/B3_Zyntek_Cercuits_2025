"""
Basic monitoring utilities (Sprint MVP)

Tracks:
- latency (seconds)
- CPU usage (%)
- memory delta (MB)

Outputs:
- JSON logs to stdout
- optional append to metrics.log
- optional Redis sink (best-effort, never breaks app)
"""
from dotenv import load_dotenv
load_dotenv()

import time
import json
import os
from datetime import datetime

import psutil

LOG_TO_FILE = os.getenv("METRICS_LOG_TO_FILE", "1") == "1"
LOG_FILE_PATH = os.getenv("METRICS_LOG_FILE", "metrics.log")

ENABLE_REDIS = os.getenv("ENABLE_REDIS_METRICS", "0") == "1"

_redis_sink = None
if ENABLE_REDIS:
    try:
        from monitoring.redis_metrics_sink import RedisMetricsSink
        _redis_sink = RedisMetricsSink(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            prefix=os.getenv("METRICS_PREFIX", "tse"),
            ttl_seconds=int(os.getenv("METRICS_TTL_SECONDS", str(7 * 24 * 3600))),
            max_list_len=int(os.getenv("METRICS_MAX_LIST_LEN", "1000")),
        )
    except Exception:
        _redis_sink = None


def monitor(step_name: str):
    """Decorator to measure latency, CPU, and memory usage for one function call."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            process = psutil.Process(os.getpid())

            start_time = time.perf_counter()
            start_mem = process.memory_info().rss / (1024 * 1024)

            result = func(*args, **kwargs)

            end_time = time.perf_counter()
            end_mem = process.memory_info().rss / (1024 * 1024)

            metrics = {
                "step": step_name,
                "latency_sec": round(end_time - start_time, 4),
                "memory_mb_delta": round(end_mem - start_mem, 2),
                "cpu_percent": psutil.cpu_percent(interval=None),
                "timestamp": datetime.utcnow().isoformat(),
            }

            _log_metrics(metrics)
            return result

        return wrapper

    return decorator


def _log_metrics(metrics: dict):
    # Always log locally
    print(json.dumps(metrics))
    if LOG_TO_FILE:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(metrics) + "\n")

    # Best-effort Redis sink (never break ingestion/inference)
    if _redis_sink is not None:
        try:
            _redis_sink.write(metrics)
        except Exception:
            pass

def log_cost_for_text(step_name: str, text: str, expected_output_tokens: int = 0):
    from AI.monitoring.cost_estimation import estimate_cost_from_text

    estimate = estimate_cost_from_text(text, expected_output_tokens=expected_output_tokens)
    metrics = {
        "step": step_name,
        "estimated_input_tokens": estimate.input_tokens,
        "estimated_output_tokens": estimate.output_tokens,
        "estimated_total_tokens": estimate.total_tokens,
        "estimated_cost_usd": estimate.estimated_cost_usd,
        "model": estimate.model_name,
        "timestamp": datetime.utcnow().isoformat(),
    }
    _log_metrics(metrics)
