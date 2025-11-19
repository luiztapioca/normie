from typing import final
import os


@final
class Config:
    """Defines useful variables throughout the application"""
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    IGNORE_LIST: str = os.path.join(BASEDIR, "IGNORE_LIST.txt")
    FORCE_LIST: str = os.path.join(BASEDIR, "FORCE_LIST.txt")

    # Redis Configuration
    REDIS_PORT: int = 6379
    REDIS_HOST: str = "localhost"
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_USER: str = "default"
    REDIS_PASSWORD: str = ""
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.path.join(PROJECT_ROOT, "logs")
    ENABLE_FILE_LOGGING: bool = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"
    ENABLE_CONSOLE_LOGGING: bool = os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true"
