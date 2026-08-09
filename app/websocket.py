"""
双方向（プロアクティブ）リアルタイムWebSocketマネージャー
セッション管理、ユーザー名対応、AI送信完了後からの正確なタイマーを処理します。
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

from config import settings
from prompts.system_prompts import get_system_prompt
from app.inference import inference_engine

logger = logging.getLogger(__name__)

class UserSession:
    """ユーザーのWebSocketセッション状態を管理するクラス"""
    def __init__(self, session_id: str, websocket: WebSocket):
        self.session_id: str = session_id
        self.websocket: WebSocket = websocket
        self.character_key: str = "nurse"
        self.user_name: str = "あなた"
        self.messages_history: list = []
        self.last_user_activity: float = time.time()
        self.proactive_task: Optional[asyncio.Task] = None
        self.is_generating: bool = False
        self.is_connected: bool = True

class ConnectionManager:
    def __init__(self):
        self.active_sessions: Dict[str, UserSession] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> UserSession:
        await websocket.accept()
        session = UserSession(session_id, websocket)
        self.active_sessions[session_id] = session
        logger.info(f"WebSocket session connected: {session_id}")
        
        self.reset_proactive_timer(session)
        return session

    def disconnect(self, session_id: str):
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.is_connected = False
            if session.proactive_task:
                session.proactive_task.cancel()
            del self.active_sessions[session_id]
            logger.info(f"WebSocket session disconnected: {session_id}")

    def reset_proactive_timer(self, session: UserSession):
        """タイマーのリセット"""
        session.last_user_activity = time.time()
        if session.proactive_task and not session.proactive_task.done():
            session.proactive_task.cancel()
        
        session.proactive_task = asyncio.create_task(
            self._proactive_timer_loop(session)
        )

    async def _proactive_timer_loop(self, session: UserSession):
        """プロアクティブ割り込みタイマー"""
        try:
            while session.is_connected:
                await asyncio.sleep(settings.HEARTBEAT_INTERVAL_SECONDS)
                
                if session.is_generating:
                    session.last_user_activity = time.time()
                    continue

                elapsed = time.time() - session.last_user_activity
                
                if elapsed >= settings.PROACTIVE_TIMEOUT_SECONDS:
                    logger.info(f"Proactive trigger activated for session [{session.session_id}] (Elapsed: {elapsed:.1f}s)")
                    
                    session.is_generating = True
                    try:
                        sys_prompt = get_system_prompt(session.character_key, user_name=session.user_name)
                        
                        response_text = inference_engine.generate_response(
                            messages=session.messages_history,
                            system_prompt=sys_prompt,
                            is_proactive=True
                        )
                        
                        session.messages_history.append({
                            "role": "assistant",
                            "content": response_text
                        })
                        
                        payload = {
                            "type": "proactive_message",
                            "sender": "ai",
                            "content": response_text,
                            "character": session.character_key,
                            "timestamp": time.time()
                        }
                        await session.websocket.send_text(json.dumps(payload, ensure_ascii=False))
                    finally:
                        session.is_generating = False
                        session.last_user_activity = time.time()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in proactive timer loop for session {session.session_id}: {e}")

    async def handle_user_message(self, session: UserSession, raw_data: str):
        """ユーザーメッセージ処理"""
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            data = {"type": "user_message", "content": raw_data}

        msg_type = data.get("type", "user_message")
        
        if "user_name" in data and data["user_name"]:
            session.user_name = data["user_name"].strip()

        if msg_type == "config_change":
            if "character" in data:
                session.character_key = data["character"]
            ack = {
                "type": "system_info",
                "content": f"設定を変更しました: キャラクター={session.character_key}, お名前={session.user_name}"
            }
            await session.websocket.send_text(json.dumps(ack, ensure_ascii=False))
            return

        user_content = data.get("content", "")
        session.messages_history.append({"role": "user", "content": user_content})

        session.is_generating = True
        try:
            sys_prompt = get_system_prompt(session.character_key, user_name=session.user_name)
            
            ai_response = inference_engine.generate_response(
                messages=session.messages_history,
                system_prompt=sys_prompt,
                is_proactive=False
            )
            
            session.messages_history.append({"role": "assistant", "content": ai_response})

            payload = {
                "type": "ai_response",
                "sender": "ai",
                "content": ai_response,
                "character": session.character_key,
                "timestamp": time.time()
            }
            await session.websocket.send_text(json.dumps(payload, ensure_ascii=False))

        except Exception as e:
            logger.error(f"Error handling user message generation: {e}")
            err_payload = {
                "type": "system_info",
                "content": f"⚠️ RunPodからの応答生成中にエラーが発生しました: {str(e)}"
            }
            await session.websocket.send_text(json.dumps(err_payload, ensure_ascii=False))
        finally:
            session.is_generating = False
            self.reset_proactive_timer(session)

manager = ConnectionManager()
