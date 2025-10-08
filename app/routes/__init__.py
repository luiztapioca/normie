from fastapi import APIRouter
from enelvo import normaliser
from ..utils import fc_list, ig_list

api = APIRouter()
norm = normaliser.Normaliser(
    fc_list=fc_list,
    ig_list=ig_list,
)


@api.get("/ping")
def ping():
    return "pong"


@api.post("/normalise")
async def do_normalise(msg: str):
    return norm.normalise(msg)
