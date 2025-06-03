from fastapi import WebSocket
from typing import Dict, List
import json
from app.core.config import WebSocketMessage

class ConnectionManager:
    def __init__(self):
        # Store connections by user_id and task_id
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, task_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][task_id] = websocket

    def disconnect(self, user_id: str, task_id: str):
        try:
            if user_id in self.active_connections:
                if task_id in self.active_connections[user_id]:
                    self.active_connections[user_id].pop(task_id)
                if not self.active_connections[user_id]:
                    self.active_connections.pop(user_id)
        except Exception:
            pass

    async def send_message(self, message: WebSocketMessage, user_id: str, task_id: str):
        try:
            if self.get_connection(user_id, task_id):
                websocket = self.active_connections[user_id][task_id]
                await websocket.send_json(message.model_dump())
        except Exception:
            self.disconnect(user_id, task_id)

    def get_connection(self, user_id: str, task_id: str) -> WebSocket:
        try:
            return self.active_connections.get(user_id, {}).get(task_id)
        except Exception:
            return None

manager = ConnectionManager() 