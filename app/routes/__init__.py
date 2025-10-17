"""Módulo de rotas do serviço"""

from crypt import methods
import uuid
import json
import logging
from flask import Blueprint
from flask.json import jsonify
from pydantic import BaseModel, Field
from redis import Redis
from ..redis import get_client, RedisError


class NormaliseRequest(BaseModel):
    msg: str = Field(min_length=1)


# normaliser = Normaliser(
#     fc_list=Config.FORCE_LIST,
#     ig_list=Config.IGNORE_LIST,
# )

api = Blueprint("api", __name__)


@api.post("/enqueue", methods=["POST"])
def do_enqueue(request: NormaliseRequest):
    """Enfileira a mensagem"""
    redis = get_client()
    try:
        msg_id = str(uuid.uuid4())
        _ = redis.set(msg_id, request.msg)
        _ = redis.rpush("norm_queue", json.dumps({"id": msg_id}))

        return 200

    except RedisError as err:
        return jsonify({"error": f"{err}"}, 500)
