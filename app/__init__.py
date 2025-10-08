from fastapi import FastAPI
from .routes import api
import logging


def init(app: FastAPI):
    app.include_router(api, prefix="/api")
    logging.basicConfig()
