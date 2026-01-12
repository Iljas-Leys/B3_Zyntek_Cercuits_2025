import json
import os
from datetime import datetime
from redis import Redis


class RedisMetricsSink:
    """
    Store metrics in Redis using simple keys (NOT RedisVL index).

    Keys:
      <prefix>:metrics:last:<step>   -> last JSON blob (SET)
      <prefix>:metrics:list:<step>   -> recent JSON blobs (LPUSH + LTRIM)
      <prefix>:metrics:count:<step>  -> counter (INCR)

    TTL is applied so metrics don’t grow forever.
    """

    def __init__(
        self,
        redis_url: str | None = None,
        prefix: str = "tse",
        ttl_seconds: int = 7 * 24 * 3600,   # 7 days
        max_list_len: int = 1000,
    ):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.prefix = prefix
        self.ttl_seconds = ttl_seconds
        self.max_list_len = max_list_len

        self.client = Redis.from_url(self.redis_url, decode_responses=True)

    def write(self, metrics: dict) -> None:
        step = metrics.get("step", "unknown")

        payload = dict(metrics)
        payload["timestamp"] = payload.get("timestamp") or datetime.utcnow().isoformat()
        raw = json.dumps(payload)

        last_key = f"{self.prefix}:metrics:last:{step}"
        list_key = f"{self.prefix}:metrics:list:{step}"
        count_key = f"{self.prefix}:metrics:count:{step}"

        pipe = self.client.pipeline(transaction=False)

        pipe.set(last_key, raw, ex=self.ttl_seconds)

        pipe.lpush(list_key, raw)
        pipe.ltrim(list_key, 0, self.max_list_len - 1)
        pipe.expire(list_key, self.ttl_seconds)

        pipe.incr(count_key)
        pipe.expire(count_key, self.ttl_seconds)

        pipe.execute()
