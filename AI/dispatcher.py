import logging

from AI.date_resolver import resolve_task_dates

from AI.handlers.shift_handler import shift_handler
from AI.handlers.absence_handler import absence_handler
from AI.handlers.late_handler import late_handler
from AI.handlers.preference_handler import preference_handler
from AI.handlers.question_handler import question_handler
from AI.handlers.memo_handler import memo_handler
from AI.handlers.other_handler import other_handler

logger = logging.getLogger(__name__)

ERROR_REPLY = (
    "処理中にエラーが起きました．"
    "お手数ですが，もう一度送るか，店長に連絡してください．"
)

HANDLERS = {
    "shift": shift_handler,
    "absence": absence_handler,
    "late": late_handler,
    "preference": preference_handler,
    "question": question_handler,
    "memo": memo_handler,
    "other": other_handler,
}

# type ごとに許可する action(プロンプトの定義と一致させる)
EXPECTED_ACTION = {
    "shift": "write",
    "absence": "write",
    "late": "write",
    "preference": "write",
    "memo": "write",
    "question": "read",
    "other": None,
}

def dispatch(user_id, task):
    """1件のtaskを対応するhandlerへ振り分け返信文を返す"""

    task_type = task.get("type")
    action = task.get("action")

    handler = HANDLERS.get(task_type)
    if handler is None:
        logger.error("Unknown task type: %r", task)
        return ERROR_REPLY

    if action != EXPECTED_ACTION[task_type]:
        logger.error("Invalid action for %s: %r", task_type, task)
        return ERROR_REPLY

    try:
        return handler(user_id, task)
    except Exception:
        logger.exception("Handler failed: type=%s", task_type)
        return ERROR_REPLY


def dispatch_tasks(user_id, data):
    """
    AIの解析結果を受け取り日付を一括変換してから，各handlerで処理し返信文をまとめる
    """
    # 日付を一括変換
    data = resolve_task_dates(data)

    tasks = data.get("tasks") if isinstance(data, dict) else data

    if not isinstance(tasks, list):
        logger.error("tasks is not a list: %r", tasks)
        return ERROR_REPLY

    results = []

    for task in tasks:
        if not isinstance(task, dict):
            logger.error("Invalid task: %r", task)
            results.append(ERROR_REPLY)
            continue

        # 日付を解決できなかった場合は登録処理を行わない
        date_error = task.get("date_error")
        if date_error:
            results.append(
                f"【日付の確認】\n{date_error}\n"
                "何月何日か確認して，もう一度送ってください．"
            )
            continue

        result = dispatch(user_id, task)

        if result:
            results.append(str(result))

    return "\n".join(results)