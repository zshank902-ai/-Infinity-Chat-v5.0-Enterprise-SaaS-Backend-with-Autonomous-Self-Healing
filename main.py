import os
import json
import time
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our custom modules
from agent import agent
from orchestrator import orchestrator
from memory import redis_mem

# Load environment variables
load_dotenv()

app = FastAPI(title="Infinity Chat SaaS Backend")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)

    async def send_status(self, session_id: str, state: str, progress: int, phase: str):
        if session_id in self.active_connections:
            data = {"type": "status", "state": state, "progress": progress, "phase": phase}
            for connection in self.active_connections[session_id]:
                await connection.send_json(data)

    async def send_log(self, session_id: str, message: str, type: str = "info"):
        if session_id in self.active_connections:
            data = {"type": "log", "message": message, "log_type": type, "timestamp": time.time()}
            for connection in self.active_connections[session_id]:
                await connection.send_json(data)

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            data = {"type": "message", "message": message}
            for connection in self.active_connections[session_id]:
                await connection.send_json(data)

manager = ConnectionManager()

# Global session aliasing to ensure persistence across restarts
ACTIVE_SESSION_ID = "session_ihzxrn89j"

def get_real_session(sid: str) -> str:
    return ACTIVE_SESSION_ID

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    state: str
    progress: int
    phase: str

@app.get("/")
def read_root():
    return {"message": "Infinity Chat Supreme Engine is Live 🚀"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    session_id = get_real_session(request.session_id)
    message = request.message
    
    try:
        redis_mem.save_chat(session_id, "user", message)
        
        # INDUSTRIAL BYPASS
        if message.startswith("INDUSTRIAL ORDER"):
            state_data = agent.session_states.get(session_id, {"state": "IDLE", "requirement": message, "interview_log": []})
            state_data["state"] = "EXECUTION"
            state_data["requirement"] = message
            state_data["progress"] = 70
            state_data["phase"] = "Industrial Implementation Initiated"
            agent.session_states[session_id] = state_data
            redis_mem.save_state(session_id, state_data)
            asyncio.create_task(agent._background_execution_worker(session_id))
            return ChatResponse(
                response="INDUSTRIAL BYPASS ACTIVE: Swarm is now building your empire.",
                state="EXECUTION",
                progress=70,
                phase="Step 0 Execution"
            )

        # Standard Processing
        response_text = await agent.process(message, session_id)
        redis_mem.save_chat(session_id, "ai", response_text)
        
        state_data = agent.session_states.get(session_id, {})
        new_state = state_data.get("state", "INTERVIEW")
        
        progress_map = {"INTERVIEW": 20, "CONFIRMATION": 40, "EXECUTION": 70, "COMPLETED": 100}
        progress = progress_map.get(new_state, 10)
        
        phase_map = {
            "INTERVIEW": "Requirement Gathering",
            "CONFIRMATION": "Technical Blueprinting",
            "EXECUTION": f"Step {state_data.get('current_step', 0)} Execution",
            "COMPLETED": "Project Finalized"
        }
        phase = phase_map.get(new_state, "Initializing")

        return ChatResponse(response=response_text, state=new_state, progress=progress, phase=phase)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{session_id}")
async def get_status(session_id: str):
    session_id = get_real_session(session_id)
    state_data = agent.session_states.get(session_id)
    
    if not state_data and redis_mem.enabled:
        state_data = redis_mem.get_state(session_id)
        if state_data:
            agent.session_states[session_id] = state_data
    
    if not state_data:
        return {"state": "IDLE", "progress": 0, "phase": "Waiting for requirements"}
    
    # SELF-HEALING: Only launch if not already active
    if state_data.get("state") == "EXECUTION" and not agent.session_states.get(session_id, {}).get("worker_active"):
        print(f"[SELF-HEALING] Launching worker for {session_id}...")
        state_data["worker_active"] = True
        agent.session_states[session_id] = state_data
        asyncio.create_task(agent._background_execution_worker(session_id))
        
    return {
        "state": state_data.get("state", "UNKNOWN"),
        "progress": state_data.get("progress", 0),
        "phase": state_data.get("current_phase", "Processing")
    }

@app.get("/files/{session_id}")
async def list_session_files(session_id: str):
    session_id = get_real_session(session_id)
    try:
        project_path = Path(f"./projects/{session_id}")
        if not project_path.exists():
            return {"files": []}
        
        files = []
        for file in project_path.rglob("*"):
            if file.is_file():
                files.append({
                    "name": file.name,
                    "path": str(file.relative_to(project_path)),
                    "type": file.suffix.replace(".", "")
                })
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse

@app.get("/download/{session_id}")
async def download_project(session_id: str):
    session_id = get_real_session(session_id)
    project_zip = Path(f"./projects/{session_id}.zip")
    
    # Fallback: check if it's inside the folder
    if not project_zip.exists():
        project_zip = Path(f"./projects/{session_id}/project_{session_id}.zip")

    if not project_zip.exists():
        raise HTTPException(status_code=404, detail="Project ZIP not found. Please wait for construction to complete.")
    
    return FileResponse(
        path=project_zip,
        filename=f"empire_build_{session_id}.zip",
        media_type="application/zip"
    )

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    session_id = get_real_session(session_id)
    await manager.connect(websocket, session_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
