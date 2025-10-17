from flask import Flask
from .routes import api


def init() -> Flask:
    """Módulo que instanância o FastAPI"""
    app = Flask(__name__)

    app.register_blueprint(api, prefix="/api")

    return app
