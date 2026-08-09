# RunPod Serverless (gemma2:9b) セットアップ & 接続マニュアル

本アプリ（TwoWayChat）と RunPod Serverless 上で起動している `gemma2:9b` モデルを連携させるための手順書です。

---

## 1. あなたが RunPod 側で行う作業（2点のみ）

### ① RunPod API Key の取得
1. [RunPod Settings - API Keys](https://www.runpod.io/console/user/settings) にアクセスします。
2. **「+ API Key」** ボタンを押して新しいAPIキーを発行し、文字列（例: `rpa_xxxxxxxxxxxxxxxxxxxxxx`）をコピーします。

### ② Endpoint ID の取得
1. [RunPod Serverless Console](https://www.runpod.io/console/serverless) にアクセスします。
2. 起動中の **Runpod Worker Ollama** エンドポイントの一覧から、**Endpoint ID**（例: `vllm-abc123xyz` または `abc123xyz`）をコピーします。

> [!NOTE]
> **Secrets（暗号化設定）について**
> `gemma2:9b` は公開モデルのため、RunPodの **Create Secrets** 設定は**一切不要**です。`Edit Endpoint` 内の `OLLAMA_MODEL_NAME` が `gemma2:9b` になっていればそのまま無視して進めて問題ありません。

---

## 2. アプリ（Web画面）からの連携設定手順

1. バックエンドサーバーを起動します：
   ```bash
   python -m app.main
   ```
2. ブラウザで **`http://localhost:8000/`** にアクセスします。
3. **「⚙️ RunPod 連携設定」** タブを開きます。
   - **推論モード**: `RunPod Serverless (本番モデル: gemma2:9b)` を選択
   - **RunPod API Key**: ①で取得した `rpa_...` を入力
   - **RunPod Endpoint ID**: ②で取得した Endpoint ID を入力
   - **Ollama モデル名**: `gemma2:9b`
4. **「⚡ 接続テスト」** ボタンを押し、「🎉 RunPod 接続成功！」と表示されることを確認します。
5. **「💾 設定を保存」** ボタンを押して設定を保存します。

---

## 3. リード型チャットのテスト

1. **「💬 リード型チャット」** タブを開きます。
2. キャラクター（アヤネ、キョウコ、ルシア、ミサキなど）を選択し、メッセージを送信します。
3. **20秒間そのままメッセージを送信せずに放置** してみてください。
   - バックグラウンドのタイマーが作動し、`⚡ AI [自発語りかけ/リード]` として `gemma2:9b` が主導権を握って自発的に語りかけてくるプロアクティブ機能を体験できます。
