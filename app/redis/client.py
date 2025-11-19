from functools import lru_cache

from redis import Redis
import redis.asyncio as redis

from ..utils import Config


@lru_cache(maxsize=None)
def get_client() -> Redis:
    """Generates a Redis client that is stored
    in cache, avoiding re-instantiation

    Returns:
        Redis: Redis client
    """
    return Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        username=Config.REDIS_USER,
        password=Config.REDIS_PASSWORD if Config.REDIS_PASSWORD else None,
        decode_responses=Config.REDIS_DECODE_RESPONSES,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30,
    )

async def get_async_client() -> redis.Redis:
    """Generates an async Redis client

    Returns:
        redis.Redis: Async Redis client
    """
    return redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        username=Config.REDIS_USER,
        password=Config.REDIS_PASSWORD if Config.REDIS_PASSWORD else None,
        decode_responses=Config.REDIS_DECODE_RESPONSES,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30,
    )
