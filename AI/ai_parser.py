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


EXPECTED_ACTION = {
    "shift": {"write", "change"},
    "absence": {"write"},
    "late": {"write"},
    "preference": {"write"},
    "memo": {"write"},
    "question": {"read"},
    "other": {None},
}


def validate_task(task):
    if not isinstance(task, dict):
        raise ValueError("taskがオブジェクトではありません")

    if not all(key in task for key in ("action", "type", "ambiguity")):
        raise ValueError("taskに必須キーがありません")

    task_type = task["type"]
    action = task["action"]

    if task_type not in EXPECTED_ACTION:
        raise ValueError(f"不明なtask typeです: {task_type}")

    if action not in EXPECTED_ACTION[task_type]:
        raise ValueError(
            f"task typeとactionの組み合わせが不正です: "
            f"{task_type}, {action}"
        )

    if not isinstance(task["ambiguity"], list):
        raise ValueError("ambiguityが配列ではありません")

    # 日付
    if task.get("date") is not None and not isinstance(task["date"], str):
        raise ValueError("dateは文字列またはnullである必要があります")

    # 時刻関連
    time_fields = [
        "start_time",
        "end_time",
        "old_start_time",
        "old_end_time",
        "new_start_time",
        "new_end_time",
    ]

    for field in time_fields:
        value = task.get(field)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{field}は文字列またはnullである必要があります")


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
            validate_task(task)

        return result

    except Exception as e:
        if DEBUG:
            print(f"OpenAI Error: {e}")

        raise RuntimeError(
            "OpenAI APIによるメッセージ解析に失敗しました"
        ) from e