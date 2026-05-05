from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import time
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
from agent import agent
from memory import memory, vault, lessons
from tools import extract_text_from_pdf, extract_text_from_pptx
from fastapi import File, UploadFile, Query
from fastapi.responses import FileResponse
import shutil
import asyncio
from openai import AsyncOpenAI
from config import config
from sentinel import sentinel

app = FastAPI(title="Infinity Chat API", version="5.0")

# Enable CORS for Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RATE LIMITING STORE
request_history = {}

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    # Simple Rate Limiting (10 requests per minute)
    if client_ip not in request_history:
        request_history[client_ip] = []
    
    # Clean old timestamps
    request_history[client_ip] = [t for t in request_history[client_ip] if now - t < 60]
    
    if len(request_history[client_ip]) > 10:
        return {"error": "Too many requests. Hacker-like activity detected!"}
    
    request_history[client_ip].append(now)
    
    # Security Headers
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    state: str

@app.get("/")
def read_root():
    return {"message": "Infinity Chat Supreme Engine is Live 🚀"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    try:
        response_text = await agent.run_autonomous(request.message, request.session_id)
        new_state = agent.session_states.get(request.session_id, {}).get("state", "INTERVIEW")
        
        # Auto-upload project if zipped
        if "[ZIP:" in response_text:
            import re
            from .tools import upload_to_cloud
            zip_match = re.search(r"\[ZIP: (.*?)\]", response_text)
            if zip_match:
                zip_name = zip_match.group(1)
                zip_file = f"d:/Python Workshop/infinity_chat/projects/{zip_name}.zip"
                background_tasks.add_task(upload_to_cloud, zip_file)

        return ChatResponse(response=response_text, state=new_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    temp_path = Path(f"d:/Python Workshop/infinity_chat/data/temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    content = ""
    ext = temp_path.suffix.lower()
    
    if ext == ".pdf":
        content = extract_text_from_pdf(str(temp_path))
    elif ext == ".pptx":
        content = extract_text_from_pptx(str(temp_path))
    elif ext in [".png", ".jpg", ".jpeg"]:
        # Handle Image with Vision
        from .router import router
        content = await router.chat("What is in this image? Explain technical details for coding.", provider="gemini", image_path=str(temp_path))
    elif ext in [".py", ".js", ".java", ".html", ".css", ".txt"]:
        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        os.remove(temp_path)
        return {"error": "Bhai, ye file format allowed nahi hai!"}

    # Feed this content to the agent as part of the session history
    agent.session_states[session_id] = {
        "state": "INTERVIEW", 
        "requirement": f"File Content Loaded from {file.filename}. Context: {content[:2000]}", 
        "interview_log": [{"user": f"Uploaded {file.filename}", "ai": "Bhai, file read kar li hai! Iske basis par kya banau?"}]
    }
    
    os.remove(temp_path)
    return {"message": f"File {file.filename} processed successfully!", "preview": content[:500]}

@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    """Convert uploaded audio to text."""
    temp_path = Path(f"d:/Python Workshop/infinity_chat/data/temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        client = AsyncOpenAI(api_key=config.DEEPSEEK_KEYS[0]) # Using first key
        audio_file = open(temp_path, "rb")
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        os.remove(temp_path)
        return {"text": transcript.text}
    except Exception as e:
        if temp_path.exists(): os.remove(temp_path)
        return {"error": str(e)}

@app.get("/tts")
async def text_to_speech(text: str = Query(...)):
    """Convert text to speech audio file."""
    output_path = Path("d:/Python Workshop/infinity_chat/data/tts_output.mp3")
    try:
        client = AsyncOpenAI(api_key=config.DEEPSEEK_KEYS[0])
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        response.stream_to_file(output_path)
        return FileResponse(output_path, media_type="audio/mpeg", filename="response.mp3")
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def get_health():
    """Get real-time system stability and health status."""
    return {
        "status": sentinel.status,
        "last_check": sentinel.last_check,
        "active_providers": len(config.GROQ_KEYS) + len(config.GEMINI_KEYS) + len(config.DEEPSEEK_KEYS),
        "errors": sentinel.errors[-5:] # Show last 5 errors
    }

@app.on_event("startup")
async def startup_event():
    # Start the Sentinel Monitor in the background safely
    asyncio.create_task(sentinel.monitor_loop())

@app.get("/projects")
def get_projects():
    """List all completed projects and their summaries."""
    return vault.get_all_summaries()

@app.get("/lessons")
def get_lessons():
    """Get all technical lessons learned by the AI."""
    return lessons.get_all_lessons()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
