from fastapi import APIRouter
from enelvo import normaliser
from ..utils import Config

api = APIRouter()
norm = normaliser.Normaliser(
    fc_list=list(Config.FORCE_LIST),
    ig_list=list(Config.IGNORE_LIST),
)


@api.get("/ping")
def ping():
    return "pong"


@api.post("/normalise")
async def do_normalise(msg: str):
    return str(norm.normalise(msg))
