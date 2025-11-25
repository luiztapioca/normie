"""Service routes module"""

import json
import uuid
from redis.asyncio import Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from ..redis import get_async_client
from redis.exceptions import RedisError
from ..utils import EnqueueRequest

api = APIRouter()


@api.post("/enqueue")
async def do_enqueue(
    request: EnqueueRequest,
    redis:Redis=Depends(get_async_client)
):
    """Enqueues the message"""
    msg = request.msg

    if not msg.strip():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail={"error": "msg is required"}
        )

    try:
        msg_id = str(uuid.uuid4())
        await redis.set(msg_id, msg)
        await redis.rpush("norm_queue_in", json.dumps({"id": msg_id, "msg": msg}))
        await redis.hset("msg_index", msg_id, "norm_queue_in")

        return JSONResponse(status_code=HTTP_202_ACCEPTED, content={"msg_id": msg_id})

    except RedisError as err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": err}
        ) from err

@api.get("/dequeue/{msg_id}")
async def dequeue(
    msg_id,
    redis: Redis=Depends(get_async_client)
):
    """_summary_

    Args:
        msg_id (_type_): _description_
        redis (Redis, optional): _description_. Defaults to Depends(get_async_client).

    Raises:
        HTTPException: _description_
    """
    try:
        msg = await redis.hget("msg_index", msg_id)
        print(msg)
    except RedisError as err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": err}
        ) from err
