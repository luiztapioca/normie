from redis import Redis
from functools import lru_cache
from ..utils import Config

@lru_cache
def get_redis() -> Redis:
    return Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=Config.REDIS_DECODE_RESPONSES
    )
