""" Módulo responsável por armazenar instanciação do cliente Redis """
from redis import Redis
from ..utils import Config

r = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=Config.REDIS_DECODE_RESPONSES
)
