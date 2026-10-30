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
                "content": user_text,
                "ambiguity": []
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

        raise RuntimeError(
            "OpenAI APIによるメッセージ解析に失敗しました"
        ) from e

    try:
        result = json.loads(response.output_text)

        # 最上位の形式を確認
        if not isinstance(result, dict):
            raise ValueError("出力がJSONオブジェクトではありません")

        if not isinstance(result.get("tasks"), list):
            raise ValueError("tasksが配列ではありません")

        # 各taskの最低限の形式を確認
        for task in result["tasks"]:
            if not isinstance(task, dict):
                raise ValueError("taskがオブジェクトではありません")

            if not all(key in task for key in ("action", "type", "ambiguity")):
                raise ValueError("taskに必須キーがありません")

            if not isinstance(task["ambiguity"], list):
                raise ValueError("ambiguityが配列ではありません")

        return result

    except Exception as e:
        if DEBUG:
            print(f"OpenAI Error: {e}")

        raise RuntimeError(
            "OpenAI APIによるメッセージ解析に失敗しました"
        ) from e