from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_log(self, session_id: str, message: str, type: str = "info"):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "log",
                    "message": message,
                    "log_type": type,
                    "timestamp": asyncio.get_event_loop().time()
                })
            except:
                self.disconnect(session_id)

    async def send_status(self, session_id: str, state: str, progress: int, phase: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "status",
                    "state": state,
                    "progress": progress,
                    "phase": phase
                })
            except:
                self.disconnect(session_id)

manager = ConnectionManager()
