from redis import Redis
from redisvl.index import SearchIndex

client = Redis.from_url("redis://localhost:6379")
index = SearchIndex.from_yaml("redisSchema.yaml", redis_client = client, validate_on_load = True)
index.create(overwrite=True)
