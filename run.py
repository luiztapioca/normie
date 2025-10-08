import uvicorn
from app import init

if __name__ == "__main__":
    app = init()
    uvicorn.run(app, host="127.0.0.1", port=8000)
