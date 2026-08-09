"""
推論エンジンモジュール (RunPod Serverless Ollama & Mockハイブリッド)
セフレ・リード型対話生成を行います（セリフのみ抽出・短文テンポ重視後処理付き）。
"""

import re
import logging
import json
import httpx
from typing import List, Dict, Optional, Tuple
from config import settings

logger = logging.getLogger(__name__)

def clean_dialogue_only(text: str) -> str:
    """
    *行動描写* や (心理描写) などのト書き・地の文を自動的に取り除き、
    純粋な会話（セリフ）のみを抽出・整形するフィルター関数
    """
    if not text:
        return ""
    
    # *...* で囲まれた行動描写の削除
    cleaned = re.sub(r'\*.*?\*', '', text)
    # ( ... ) や （ ... ） で囲まれたト書きの削除
    cleaned = re.sub(r'\(.*?\)', '', cleaned)
    cleaned = re.sub(r'（.*?）', '', cleaned)
    # ［ ... ］ や [ ... ] の削除
    cleaned = re.sub(r'\[.*?\]', '', cleaned)
    cleaned = re.sub(r'［.*?］', '', cleaned)
    
    # 連続する空白や改行の整理
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    result = " ".join(lines).strip()
    
    if not result:
        result = text.replace("*", "").strip()
        
    return result

class MatrixInferenceEngine:
    def __init__(self):
        pass

    def test_runpod_connection(self, api_key: str, endpoint_id: str, model_name: str) -> Tuple[bool, str]:
        """RunPod Serverless エンドポイントへの接続テスト"""
        if not api_key or not endpoint_id:
            return False, "API Key と Endpoint ID を入力してください。"

        url = f"https://api.runpod.ai/v2/{endpoint_id}/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name or "gemma2:9b",
            "messages": [
                {"role": "user", "content": "Hello! Test connection."}
            ],
            "max_tokens": 10
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    return True, "RunPod 接続成功！サーバーレスモデルが準備完了状態です。"
                
                runsync_url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
                runsync_payload = {
                    "input": {
                        "api": {"name": "chat", "args": {"model": model_name, "messages": [{"role": "user", "content": "Test"}]}}
                    }
                }
                resp2 = client.post(runsync_url, headers=headers, json=runsync_payload)
                if resp2.status_code == 200:
                    return True, "RunPod (runsync) 接続成功！"

                return False, f"RunPod HTTP エラー ({resp.status_code}): {resp.text}"

        except Exception as e:
            return False, f"接続エラー: {str(e)}"

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_new_tokens: int = 120,  # 短文テンポ重視のためトークン数を120に制限
        temperature: float = 0.7,
        is_proactive: bool = False
    ) -> str:
        """
        システムプロンプト ＋ 会話履歴でテキスト生成（後処理でセリフのみ抽出）
        """
        if settings.INFERENCE_MODE == "runpod" and settings.RUNPOD_API_KEY and settings.RUNPOD_ENDPOINT_ID:
            try:
                raw_response = self._generate_runpod(
                    messages=messages,
                    system_prompt=system_prompt,
                    max_tokens=max_new_tokens,
                    temperature=temperature,
                    is_proactive=is_proactive
                )
                # 地の文・ト書きを除去して純粋なセリフのみ返却
                return clean_dialogue_only(raw_response)
            except Exception as e:
                logger.error(f"RunPod inference failed ({e}). Falling back to Mock mode.")
                return self._generate_mock_response(system_prompt, is_proactive)
        else:
            return self._generate_mock_response(system_prompt, is_proactive)

    def _generate_runpod(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        is_proactive: bool
    ) -> str:
        """RunPod Serverless Ollama エンドポイントの呼び出し"""
        url = f"https://api.runpod.ai/v2/{settings.RUNPOD_ENDPOINT_ID}/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        }

        full_messages = [{"role": "system", "content": system_prompt}] + list(messages)

        if is_proactive:
            full_messages.append({
                "role": "system",
                "content": (
                    "[プロアクティブ自発リード指示]\n"
                    "ユーザーの応答を待たず、あなたから会話をリードするターンです。\n"
                    "「黙っていないで返事して」といった単なる催促・注意は禁止します。\n"
                    "これまでの会話の内容を踏まえ、あなたから次の話の展開・甘い提案・焦らしの問いかけを短く（1〜2文セリフのみ）投げかけて相手をリードしてください。"
                )
            })

        payload = {
            "model": settings.OLLAMA_MODEL_NAME or "gemma2:9b",
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        logger.info(f"Sending request to RunPod OpenAI API (max_tokens={max_tokens}): {settings.OLLAMA_MODEL_NAME}")

        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    result = resp.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        choice = result["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            return choice["message"]["content"].strip()
                        elif "text" in choice:
                            return choice["text"].strip()
                    elif "output" in result:
                        out = result["output"]
                        if isinstance(out, dict):
                            if "choices" in out and len(out["choices"]) > 0:
                                return out["choices"][0]["message"]["content"].strip()
                            elif "response" in out:
                                return out["response"].strip()
                        elif isinstance(out, str):
                            return out.strip()

                # runsync フォールバック
                runsync_url = f"https://api.runpod.ai/v2/{settings.RUNPOD_ENDPOINT_ID}/runsync"
                runsync_payload = {
                    "input": {
                        "api": {
                            "name": "chat",
                            "args": {
                                "model": settings.OLLAMA_MODEL_NAME,
                                "messages": full_messages,
                                "stream": False
                            }
                        }
                    }
                }
                
                resp_rs = client.post(runsync_url, headers=headers, json=runsync_payload)
                if resp_rs.status_code == 200:
                    res_data = resp_rs.json()
                    if "output" in res_data:
                        out = res_data["output"]
                        if isinstance(out, dict):
                            if "message" in out and "content" in out["message"]:
                                return out["message"]["content"].strip()
                            elif "response" in out:
                                return out["response"].strip()
                            elif "choices" in out and len(out["choices"]) > 0:
                                return out["choices"][0]["message"]["content"].strip()
                        elif isinstance(out, str):
                            return out.strip()
                        return json.dumps(out, ensure_ascii=False)

                raise RuntimeError(f"RunPod API error: OpenAI Code={resp.status_code}, runsync Code={resp_rs.status_code}")

        except Exception as e:
            logger.error(f"Error calling RunPod API: {e}", exc_info=True)
            raise RuntimeError(f"RunPod通信/生成エラー: {str(e)}")

    def _generate_mock_response(self, system_prompt: str, is_proactive: bool) -> str:
        """モックモード用応答生成"""
        char_name = "AI"
        if "アヤネ" in system_prompt:
            char_name = "アヤネ"
        elif "キョウコ" in system_prompt:
            char_name = "キョウコ"
        elif "ゆい" in system_prompt:
            char_name = "ゆい"
        elif "ミサキ" in system_prompt:
            char_name = "ミサキ"

        if is_proactive:
            return f"さっきの話の続きだけど、次はどうしてほしい？私の目を見て、素直に言ってごらん。"
        else:
            return f"ちゃんと私の目を見て？あなたの欲しいもの、全部お見通しなんだから…素直になりなさい。"

inference_engine = MatrixInferenceEngine()
