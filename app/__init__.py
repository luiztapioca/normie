from fastapi import FastAPI
from .routes import api
from .utils.logging_config import setup_logging
from .utils.config import Config


def init() -> FastAPI:
    """Initializes FastAPI"""
    setup_logging(
        log_level=Config.LOG_LEVEL,
        log_dir=Config.LOG_DIR,
        enable_file_logging=Config.ENABLE_FILE_LOGGING,
        enable_console_logging=Config.ENABLE_CONSOLE_LOGGING
    )
    
    app = FastAPI(title="Normie")

    app.include_router(api, prefix="/api")

    return app
