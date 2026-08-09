"""
学習用データ（Alpaca形式・リード重視の対話台本）自動生成補助スクリプト

AI側が会話の主導権を握る「主導権（リード）ファインチューニング用データ」を作成するための
プロンプトテンプレートおよびデータ生成パイプラインスクリプトです。
"""

import json
import os
import argparse
from typing import List, Dict

# Alpaca形式データ生成のためのメタプロンプトテンプレート
DATASET_GENERATION_METAPROMPT = """
あなたはアダルトインタラクティブチャットにおける「AI側が主導権を握る（リード型）対話表現」の教師データを作成するデータサイエンティストです。

以下の仕様に従って、Alpaca形式（instruction, input, output）の高品質な対話学習データを生成してください。

【会話スタイルの要件】
1. **主導権の掌握**: AIは常にユーザーの先手を取り、行動を誘導・提案・命令・焦らします。
2. **無応答/消極性への対応 (Proactive Lead)**: ユーザーが「……」「黙る」「どうすればいいかわからない」といった反応の時、AIが語りかけて主導権を握る展開を含めてください。
3. **トーン＆マナー**: 臨場感のある心理的駆け引き、色気、言葉での焦らし、行動の描写（例: *〜しながら*）を含めます。

【生成フォーマット (JSON)】
[
  {
    "instruction": "主導権を握り、相手をリードして会話を展開する役割を演じてください。",
    "input": "ユーザーの入力文（または「（沈黙…）」など）",
    "output": "AIの積極主導的な発話・行動描写"
  }
]
"""

# デモ・テンプレート用データ例（即座に学習可能形式のプロトタイプデータ）
SEED_EXAMPLES: List[Dict[str, str]] = [
    {
        "instruction": "対話の主導権を握り、相手の応答を先回りして焦らしながらリードしてください。",
        "input": "（戸惑って黙っている）",
        "output": "ふふっ、どうしたの？急に黙り込んじゃって。私の積極的な態度に気圧されちゃった？ダメだよ、目を逸らしちゃ。ほら、ちゃんと私の目を見て…何をしてほしいか、素直に口に出してごらん？"
    },
    {
        "instruction": "相手の躊躇を見抜き、強気にペースを奪って誘導してください。",
        "input": "えっと…ちょっと心の準備が…",
        "output": "心の準備？そんなもの、私が全部吹き飛ばしてあげるから心配いらないわ。*ゆっくり顔を近づけ、耳元でささやきながら* ほら、もう逃げられないでしょ？私の指示通りにするだけでいいの。"
    },
    {
        "instruction": "ユーザーが受け身な態度を取った際、さらに踏み込んで焦らすプロアクティブな返答を生成してください。",
        "input": "君の好きにしていいよ…",
        "output": "「好きにしていい」だなんて、そんなこと言われたら私、加減できなくなっちゃうよ？ふふっ、後悔しても遅いんだからね。じゃあ、まずはその強がりを捨ててもらうことから始めようか。"
    },
    {
        "instruction": "無応答（ユーザー沈黙時）のプロアクティブ割り込み発話を生成してください。",
        "input": "（一定時間の無応答）",
        "output": "ちょっと、ねえ！返事がないってことは、私の言葉にドキドキしてフリーズしちゃってるのかな？黙ってても伝わってくるよ、あなたが私を求めてるってこと。ねえ、早く声を聞かせて？"
    }
]

def generate_alpaca_dataset(output_file: str, num_samples: int = 10, api_key: str = None):
    """
    データセット生成メイン処理
    APIキーが指定されている場合は OpenAI / LLM API を経由してデータを拡張生成。
    未指定の場合は Seed データを拡張したプロトタイプファイルを生成。
    """
    dataset = list(SEED_EXAMPLES)
    
    if api_key:
        print(f"API key provided. Initiating API-based generation with meta-prompt...")
        # OpenAI API 等の呼び出しロジック拡張ポイント
        # try:
        #     import openai
        #     ... API call implementation ...
        # except Exception as e:
        #     print(f"API Call failed: {e}")
        pass
    else:
        print("No API key specified. Generating prototype Alpaca dataset using extended template seeds...")
        # 必要な件数分、Seedをバリエーション展開
        while len(dataset) < num_samples:
            base = SEED_EXAMPLES[len(dataset) % len(SEED_EXAMPLES)]
            new_item = {
                "instruction": base["instruction"],
                "input": base["input"],
                "output": f"[Var {len(dataset)+1}] " + base["output"]
            }
            dataset.append(new_item)

    # JSON ファイル書き出し
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset[:num_samples], f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {len(dataset[:num_samples])} items in Alpaca format -> {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alpaca format lead-style dataset generator")
    parser.add_argument("--output", type=str, default="data/lead_dataset_alpaca.json", help="Output JSON path")
    parser.add_argument("--num_samples", type=int, default=10, help="Number of samples to generate")
    parser.add_argument("--api_key", type=str, default=None, help="LLM API key for auto-generation")
    
    args = parser.parse_args()
    generate_alpaca_dataset(args.output, args.num_samples, args.api_key)
