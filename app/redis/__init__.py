"""Module responsible for storing Redis client instantiation"""
from redis.exceptions import RedisError
from .client import get_client, get_async_client
