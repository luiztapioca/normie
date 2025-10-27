from pydantic import BaseModel

class EnqueueRequest(BaseModel):
    """Model para recebimento de mensagens em '/api/enqueue'"""
    msg: str
