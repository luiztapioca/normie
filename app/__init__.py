import logging
from fastapi import FastAPI
from .utils import Config
from .routes import api


def init() -> FastAPI:
    app = FastAPI()

    app.include_router(api, prefix="/api")
    logging.basicConfig()

    return app
