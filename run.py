from fastapi import FastAPI
import uvicorn
from app import init

app = FastAPI()
init(app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
