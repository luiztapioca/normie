from fastapi import FastAPI
from .routes import api
import logging


def init() -> FastAPI:
    app = FastAPI()
    app.include_router(api, prefix="/api")
    logging.basicConfig()

    return app
