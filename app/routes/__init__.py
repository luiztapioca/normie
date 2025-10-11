""" Módulo de rotas do serviço """
import uuid
import json
import logging
from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field
from redis import Redis
from ..redis import get_client, RedisError


class NormaliseRequest(BaseModel):
    msg: str = Field(min_length=1)


class NormaliseResponse(BaseModel):
    id: uuid.UUID
    status: str
    msg: str

# normaliser = Normaliser(
#     fc_list=Config.FORCE_LIST,
#     ig_list=Config.IGNORE_LIST,
# )

api = APIRouter()

@api.post("/enqueue")
def do_enqueue(request: NormaliseRequest,redis:Redis=Depends(get_client)):
    """Enfileira a mensagem"""
    try:
        msg_id = str(uuid.uuid4())
        redis.set(msg_id, request.msg)
        redis.rpush("norm_queue", json.dumps({"id": msg_id}))
        logging.info("Mensagem enfileirada: %s", msg_id)

        return NormaliseResponse(
            id=msg_id,
            status="enqueued",
            msg=request.msg
        )

    except RedisError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {err}"
        ) from err
