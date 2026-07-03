from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import json

from AI.Prompts.shiftbot_prompt import SHIFTBOT_PROMPT

# .env読み込み
env_path = Path(__file__).resolve().parent.parent / "Config" / ".env"
load_dotenv(env_path)

# OpenAIクライアント
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# デバッグモード
DEBUG = True


def other_task(user_text):
    """AIが解析できなかった場合のフォールバック"""
    return {
        "tasks": [
            {
                "action": None,
                "type": "other",
                "content": user_text
            }
        ]
    }


def parse_message(user_text):
    """
    ユーザーのメッセージを解析し、
    JSON(dict)として返す。
    """


    try:
        response = client.responses.create(
            model="gpt-5.4-mini",
            instructions=SHIFTBOT_PROMPT,
            input=user_text
        )

        if DEBUG:
            print("\n===== AI出力 =====")
            print(response.output_text)
            print()

    except Exception as e:
        if DEBUG:
            print(f"OpenAI Error: {e}")

        return other_task(user_text)

    try:
        return json.loads(response.output_text)

    except json.JSONDecodeError as e:
        if DEBUG:
            print(f"JSON Decode Error: {e}")

        return other_task(user_text)