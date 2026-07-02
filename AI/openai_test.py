from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv
import json

from Prompts.shiftbot_prompt import SHIFTBOT_PROMPT

# .env 読み込み
env_path = Path(__file__).resolve().parent.parent / "Config" / ".env"
load_dotenv(env_path)

# クライアント作成（環境変数から取得）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# API呼び出し
while True:
    user_input = input("入力> ")

    if user_input.lower() == "exit":
        break

    try:
        response = client.responses.create(
            model="gpt-5.4-mini",
            instructions=SHIFTBOT_PROMPT,
            input=user_input
        )

        result = json.loads(response.output_text)

        print("\n===== AI出力 =====")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        print()

    except Exception as e:
        print(f"\nエラー: {e}")
