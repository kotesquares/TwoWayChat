"""
FastAPI アプリケーションエントリーポイント
REST API, RunPod設定コントロール, WebSocket通信, 統合WebコンソールUIを提供します。
"""

import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import settings
from prompts.system_prompts import CHARACTER_PROMPTS
from app.inference import inference_engine
from app.websocket import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TwoWayChat")

app = FastAPI(
    title="Proactive Lead AI Chat Backend Console",
    description="RunPod Serverless (gemma2:9b) 対応 プロアクティブリードチャットバックエンド",
    version="1.0.0"
)

class ConfigUpdateRequest(BaseModel):
    inference_mode: str
    runpod_api_key: str
    runpod_endpoint_id: str
    ollama_model_name: str
    proactive_timeout_seconds: float

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "inference_mode": settings.INFERENCE_MODE,
        "model": settings.OLLAMA_MODEL_NAME
    }

@app.get("/api/config")
def get_config():
    return {
        "inference_mode": settings.INFERENCE_MODE,
        "runpod_api_key": settings.RUNPOD_API_KEY,
        "runpod_endpoint_id": settings.RUNPOD_ENDPOINT_ID,
        "ollama_model_name": settings.OLLAMA_MODEL_NAME,
        "proactive_timeout_seconds": settings.PROACTIVE_TIMEOUT_SECONDS
    }

@app.post("/api/config")
def update_config(req: ConfigUpdateRequest):
    settings.INFERENCE_MODE = req.inference_mode
    settings.RUNPOD_API_KEY = req.runpod_api_key.strip()
    settings.RUNPOD_ENDPOINT_ID = req.runpod_endpoint_id.strip()
    settings.OLLAMA_MODEL_NAME = req.ollama_model_name.strip()
    settings.PROACTIVE_TIMEOUT_SECONDS = req.proactive_timeout_seconds
    settings.save_to_file()
    return {"status": "success", "message": "設定を保存しました。"}

@app.post("/api/config/test")
def test_connection(req: ConfigUpdateRequest):
    success, msg = inference_engine.test_runpod_connection(
        api_key=req.runpod_api_key.strip(),
        endpoint_id=req.runpod_endpoint_id.strip(),
        model_name=req.ollama_model_name.strip()
    )
    return {"success": success, "message": msg}

@app.get("/api/characters")
def list_characters():
    return {
        key: {"name": info["name"], "role": info["role"]} 
        for key, info in CHARACTER_PROMPTS.items()
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    session = await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.handle_user_message(session, data)
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error in session {session_id}: {e}")
        manager.disconnect(session_id)

@app.get("/")
def get_console_ui():
    """統合Webコンソール (index.html から静的サービング)"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    return FileResponse(template_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
