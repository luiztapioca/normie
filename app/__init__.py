import logging
from fastapi import FastAPI
from .utils import Config
from .routes import api


def init() -> FastAPI:
    """ Módulo que instanância o FastAPI """
    app = FastAPI()

    app.include_router(api, prefix="/api")

    return app
