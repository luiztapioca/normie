from fastapi import APIRouter
from enelvo.normaliser import Normaliser
from ..utils import Config

api = APIRouter()
normaliser = Normaliser(
    fc_list=Config.FORCE_LIST,
    ig_list=Config.IGNORE_LIST,
)


@api.get("/ping")
def ping():
    return "pong"


@api.post("/normalise")
async def do_normalise(msg: str):
    return {"result": normaliser.normalise(msg)}
