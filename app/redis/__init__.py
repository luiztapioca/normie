""" Módulo responsável por armazenar instanciação do cliente Redis """
from redis.exceptions import RedisError
from .client import get_client

__all__ = ["RedisError", "get_client"]
