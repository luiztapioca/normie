from pydantic import BaseModel

class EnqueueRequest(BaseModel):
    msg: str
