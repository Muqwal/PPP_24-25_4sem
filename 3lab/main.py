from fastapi import FastAPI
from app.websocket.routes import router as websocket_router

app = FastAPI(title="Huffman Coding WebSocket Service")

app.include_router(websocket_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 