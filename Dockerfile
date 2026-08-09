# Python 3.11 Slim ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポートの公開 (デフォルト 8000 / RenderなどのPORT環境変数に対応)
ENV PORT=8000
EXPOSE 8000

# uvicorn サーバーの起動
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
