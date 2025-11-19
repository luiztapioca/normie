"""Service routes module"""

import json
import uuid
from redis import Redis

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
async def do_enqueue(request: EnqueueRequest, redis:Redis=Depends(get_client)):
    """Enqueues the message"""
    msg = request.msg

    if not msg.strip():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail={"error": "msg is required"}
        )

    try:
        msg_id = str(uuid.uuid4())
        _ = redis.set(msg_id, msg)
        _ = redis.rpush("norm_queue_in", json.dumps({"id": msg_id, "msg": msg}))

        return JSONResponse(status_code=HTTP_202_ACCEPTED, content={"msg_id": msg_id})

    except RedisError as err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": err}
        ) from err
