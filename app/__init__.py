from fastapi import FastAPI
from .routes import api


def init() -> FastAPI:
    """Inicializa o FastAPI com logging configurado"""
    app = FastAPI(title="Normie")

    app.include_router(api, prefix="/api")

    return app
