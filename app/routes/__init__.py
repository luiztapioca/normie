""" Módulo de rotas do serviço """
import uuid
import json
from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field
from enelvo.normaliser import Normaliser
from ..utils import Config
from ..redis import get_redis, RedisError


class NormaliseRequest(BaseModel):
    msg: str = Field(min_length=1)


class NormaliseResponse(BaseModel):
    id: uuid.UUID
    status: str
    msg: str

api = APIRouter()
normaliser = Normaliser(
    fc_list=Config.FORCE_LIST,
    ig_list=Config.IGNORE_LIST,
)


@api.post("/enqueue")
def do_enqueue(request: NormaliseRequest,redis=Depends(get_redis)):
    """Enfileira a mensagem"""
    try:
        msg_id = uuid.uuid4()
        redis.set(str(msg_id), request.msg)
        redis.rpush("norm_queue", json.dumps({"id": str(msg_id)}))

        return NormaliseResponse(
            id=msg_id,
            status="enqueued",
            msg=request.msg
        )

    except RedisError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro de armazenamento: {err}"
        ) from err
