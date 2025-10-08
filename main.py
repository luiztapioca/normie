import logging
from app.routes import api
from fastapi import FastAPI
import uvicorn


def init() -> FastAPI:
    app = FastAPI()
    app.include_router(api, prefix="/api")
    return app


def serve():
    logging.basicConfig()
    app = init()

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    serve()
