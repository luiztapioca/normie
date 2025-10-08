from fastapi import APIRouter

api = APIRouter()


@api.get("/ping")
def ping():
    return "pong"


@api.post("/normalise")
def normaliser(msg: str):
    return
