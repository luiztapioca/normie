from fastapi import APIRouter
from pydantic import BaseModel
from enelvo.normaliser import Normaliser
from ..utils import Config


class NormaliseRequest(BaseModel):
    msg: str


api = APIRouter()
normaliser = Normaliser(
    fc_list=Config.FORCE_LIST,
    ig_list=Config.IGNORE_LIST,
)


@api.get("/ping")
def ping():
    return "pong"


@api.post("/enqueue")
def do_enqueue(request: NormaliseRequest):
    return {"result": normaliser.normalise(request.msg)}
