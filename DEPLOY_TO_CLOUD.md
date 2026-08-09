# チャットWebアプリ クラウド無料デプロイ手順書 (Render編)

PCを起動しておかなくても、スマホや別の端末のブラウザから **専用のURL**（`https://twowaychat-xxxx.onrender.com`）を開くだけで、いつでも「ゆい」や「アヤネ」と会話・セーブ・ロードができる完全クラウド環境の構築手順です。

無料で利用でき、アダルト/NSFWなコンテンツに対しても制限のない推奨プラットフォーム **Render (render.com)** を使用します。

---

## 全体手順（3ステップ）

```
[ Step 1 ] コードを GitHub リポジトリにアップロード
    │
[ Step 2 ] Render (render.com) で無料Webサービスを作成
    │
[ Step 3 ] 発行された専用URLにスマホでアクセス＆RunPod設定入力！
```

---

## Step 1: GitHub にコードをアップロード

1. [GitHub](https://github.com/) にログインし、新しいリポジトリ（例: `TwoWayChat`）を作成します。
2. 手元のPCのターミナル（`c:/projects/TwoWayChat`）で以下を実行し、コードをプッシュします：

```bash
git init
git add .
git commit -m "Initial commit for TwoWayChat Cloud deployment"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/TwoWayChat.git
git push -u origin main
```

---

## Step 2: Render (render.com) でデプロイ

1. [Render 公式サイト (render.com)](https://render.com/) にアクセスし、**「GET STARTED FOR FREE」** から無料アカウントを作成します（GitHubアカウントでログインすると超簡単です）。
2. ダッシュボード画面右上の **「+ New」** ボタンを押し、**「Web Service」** を選択します。
3. **「Build and deploy from a Git repository」** を選択し、先ほど作成した GitHub リポジトリ `TwoWayChat` を選択（Connect）します。
4. 設定画面で以下を入力・確認します：
   * **Name**: `twowaychat`（お好きな名前）
   * **Language**: `Docker`（自動認識されます）
   * **Instance Type**: **`Free`**（完全無料枠を選択）
5. 画面一番下の **「Create Web Service」** ボタンを押します。
6. **2〜3分待つ** と、ビルドが完了して画面上部に **専用のURL**（例: `https://twowaychat.onrender.com`）が発行されます！

---

## Step 3: スマホから接続＆遊ぶ方法

1. スマホのブラウザ（SafariやChrome）で、発行されたURL **`https://twowaychat.onrender.com`** にアクセスします。
2. **「⚙️ RunPod 連携設定」** タブを開き、あなたの RunPod API Key と Endpoint ID を入力して **「💾 設定を保存」** を押します。
3. これで完了です！
   * PCの電源を切っても、いつでもスマホからこのURLを開くだけで「ゆい」や「アヤネ」と会話・プロアクティブリード・暗号化セーブ/ロードが自由に楽しめます！
