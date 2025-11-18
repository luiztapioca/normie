""" Módulo responsável por armazenar instanciação do cliente Redis """
from redis.exceptions import RedisError
from .client import get_client, get_async_client
