import os
import json
import logging
from typing import Dict, Any
from pydantic import BaseModel

CONFIG_FILE_PATH = "config.json"
logger = logging.getLogger(__name__)

class Settings(BaseModel):
    # 推論モード: "runpod" (RunPod Serverless Ollama) または "mock" (ローカル検証用)
    INFERENCE_MODE: str = "mock"
    
    # RunPod Serverless 設定
    RUNPOD_API_KEY: str = ""
    RUNPOD_ENDPOINT_ID: str = ""
    OLLAMA_MODEL_NAME: str = "gemma2:9b"
    
    # ローカル用ベースモデル名/パス
    BASE_MODEL_NAME_OR_PATH: str = "Qwen/Qwen2.5-7B-Instruct"
    
    # プロアクティブ（自発的語りかけ）無応答タイマー（秒）
    PROACTIVE_TIMEOUT_SECONDS: float = 30.0
    
    # WebSocketハートビート間隔（秒）
    HEARTBEAT_INTERVAL_SECONDS: float = 5.0

    def save_to_file(self, filepath: str = CONFIG_FILE_PATH):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)
            logger.info(f"Configuration saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    @classmethod
    def load_from_file(cls, filepath: str = CONFIG_FILE_PATH) -> "Settings":
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(f"Loaded config from {filepath}")
                return cls(**data)
            except Exception as e:
                logger.error(f"Failed to load config from {filepath}: {e}")
        return cls()

settings = Settings.load_from_file()
