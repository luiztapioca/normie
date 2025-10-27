"""Módulo de rotas do serviço"""

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ..redis import RedisError, get_client
from ..utils import EnqueueRequest

api = APIRouter()


@api.post("/enqueue")
async def do_enqueue(request: EnqueueRequest, redis=Depends(get_client)):
    """Enfileira a mensagem"""
    msg = request.msg

    if not msg.strip():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail={"error": "msg é obrigatório"}
        )

    try:
        msg_id = str(uuid.uuid4())
        _ = redis.set(msg_id, msg)
        _ = redis.rpush("norm_queue", json.dumps({"id": msg_id}))

        return JSONResponse(status_code=HTTP_202_ACCEPTED, content={"msg_id": msg_id})

    except RedisError as err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": err}
        ) from err
