"""Service routes module"""

import json
import uuid
from redis.asyncio import Redis
from redis.exceptions import RedisError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_202_ACCEPTED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_404_NOT_FOUND
)
from ..redis import get_async_client
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

        return JSONResponse(
            status_code=HTTP_202_ACCEPTED,
            content={"msg_id": msg_id}
        )

    except RedisError as err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": err}
        ) from err

@api.get("/dequeue/{msg_id}")
async def dequeue(
    msg_id,
    redis: Redis=Depends(get_async_client)
):
    """Retrieves a message by its ID and returns its current status and queue location
    
    Args:
        msg_id: The UUID of the message to retrieve
        redis: Redis client dependency
        
    Returns:
        JSON response with message details, queue location, and status
        
    Raises:
        HTTPException: If message not found or Redis error occurs
    """

    try:
        queue = await redis.hget("msg_index", msg_id)

        if not queue:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail={"error": f"{msg_id} not found"}
            )

        status_map = {
            "norm_queue_in": "pending",
            "norm_queue_out": "completed",
            "norm_queue_errors": "error"
        }

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "msg_id": msg_id,
                "queue": status_map.get(queue, "unknown")
            }
        )
    except RedisError as err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": err}
        ) from err
