# 双方向プロアクティブAIチャット (マトリックス型モデル設計)

AI側が会話の主導権（リード）を握り、自発的（プロアクティブ）に語りかけるアダルト向けインタラクティブチャットシステムのバックエンド & 推論パイプラインプロトタイプです。

## 1. アーキテクチャの特長

### マトリックス（組み合わせ）型モデル設計
- **「挙動・対話スタイル（LoRA）」と「キャラクター属性（システムプロンプト）」の分離**
  - **対話スタイル・テンポ (LoRA)**: `active_lead`（積極主導型）、`teasing_lead`（焦らし型）などの挙動をLoRAアダプタで動的に適用。
  - **キャラクター属性 (System Prompt)**: ナース、教師、メイド、幼馴染などの設定・職業・語尾をシステムプロンプトで動的注入。

### 双方向（プロアクティブ）発話メカニズム
- WebSocket接続上の非同期タイマー監視により、ユーザーが設定時間（例: 20秒）以上沈黙した場合、AIが自発的に主導権を握り、追撃メッセージや焦らしメッセージを送信します。

---

## 2. ディレクトリ構造

```
c:/projects/TwoWayChat/
├── README.md                 # 本ドキュメント
├── requirements.txt          # Python依存ライブラリ
├── config.py                 # システム・モデル・タイマー設定
├── prompts/
│   ├── __init__.py
│   └── system_prompts.py     # キャラクター属性システムプロンプト定義
├── app/
│   ├── __init__.py
│   ├── inference.py          # Transformers + PEFT マトリックス推論エンジン
│   ├── websocket.py          # WebSocket 接続管理 & プロアクティブタイマー
│   └── main.py               # FastAPI エントリーポイント & テストWeb UI
└── scripts/
    └── generate_dataset.py   # Alpaca形式リード対話データ自動生成スクリプト
```

---

## 3. セットアップ & 起動手順

### 1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 2. バックエンドサーバーの起動
```bash
python -m app.main
# または
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. テストUIでの動作確認
ブラウザで `http://localhost:8000/` にアクセスしてください。
- チャット画面が表示され、リアルタイムに会話が可能です。
- **キャラクター属性** や **LoRAスタイル** を画面上のドロップダウンで即座に切り替え可能です。
- メッセージを入力せずに **20秒間放置** すると、`⚡ AI [自発発話/リード]` としてAIが自発的に語りかけてくるプロアクティブ機能を体験できます。

---

## 4. 学習データセットの生成手順

Alpaca形式の対話学習データセットを作成する補助スクリプトが付属しています。

```bash
python scripts/generate_dataset.py --output data/lead_dataset_alpaca.json --num_samples 20
```

生成された `data/lead_dataset_alpaca.json` を使用して、ベースモデルに対するLoRAファインチューニング（Unsloth, Axolotl, LLaMA-Factory 等）を実行してください。

---

## 5. GPU環境での本格運用（実モデルロード）

`config.py` または環境変数にて、ベースモデルパスやLoRAアダプタのディレクトリを指定してください。

```bash
export BASE_MODEL_NAME_OR_PATH="Qwen/Qwen2.5-7B-Instruct"
export LORA_ACTIVE_LEAD="./lora_adapters/active_lead"
```

`app/inference.py` 内の `MatrixInferenceEngine` の `mock_mode=False` に設定することで、実モデル・実LoRAアダプタの動的読み込みおよび推論が有効化されます。
