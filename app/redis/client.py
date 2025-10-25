from functools import lru_cache

from redis import Redis

from ..utils import Config


@lru_cache(maxsize=None)
def get_client() -> Redis:
    """Gera um client redis que fica armazenado
    no cache, evitando a re-instanciação

    Returns:
        Redis: cliente redis
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
