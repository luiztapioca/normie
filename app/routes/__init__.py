"""Módulo de rotas do serviço"""

from crypt import methods
import uuid
import json
import logging
from flask import Blueprint, Response
from flask.json import jsonify
from pydantic import BaseModel, Field
from ..redis import get_client, RedisError


class NormaliseRequest(BaseModel):
    msg: str = Field(min_length=1)


api = Blueprint("api", __name__)


@api.post("/enqueue", methods=["POST"])
def do_enqueue(msg: str) -> tuple[Response, int]:
    """Enfileira a mensagem"""
    redis = get_client()
    try:
        msg_id = str(uuid.uuid4())
        _ = redis.set(msg_id, msg)
        _ = redis.rpush("norm_queue", json.dumps({"id": msg_id}))

        return jsonify({"id": msg_id}), 201

    except RedisError as err:
        return jsonify({"error": f"{err}"}), 500
