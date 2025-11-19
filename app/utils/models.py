from pydantic import BaseModel

class EnqueueRequest(BaseModel):
    """Model for receiving messages in '/api/enqueue'"""
    msg: str
