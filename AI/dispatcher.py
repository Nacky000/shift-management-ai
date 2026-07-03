# dispatcher.py 

# 各typeに対応するhandlerを読み込む
from AI.handlers.schedule_handler import schedule_handler
from AI.handlers.change_handler import change_handler
from AI.handlers.absence_handler import absence_handler
from AI.handlers.late_handler import late_handler
from AI.handlers.preference_handler import preference_handler
from AI.handlers.question_handler import question_handler
from AI.handlers.memo_handler import memo_handler
from AI.handlers.other_handler import other_handler

# typeごとに呼び出すhandlerを管理
handlers = {
    "schedule": schedule_handler,
    "change": change_handler,
    "absence": absence_handler,
    "late": late_handler,
    "preference": preference_handler,
    "question": question_handler,
    "memo": memo_handler,
    "other": other_handler
}


def dispatch(task):
    """
    1件のtaskを対応するhandlerへ振り分ける
    """
    
    # actionとtypeを取得
    action = task.get("action")
    task_type = task.get("type")

    # actionが存在しない場合はotherとして処理
    # if action is None:
    #     return other_handler(task)

    # typeに対応するhandlerを取得
    # 存在しないtypeの場合はother_handlerを使用
    handler = handlers.get(task_type, other_handler)

    # handlerを実行して結果を返す
    return handler(task)


def dispatch_tasks(data):
    """
    AIが返したtasksを順番にhandlerへ渡して処理する
    """

    # handlerの実行結果を格納するリスト
    results = []

    # tasks内の全てのtaskを順番に処理
    for task in data.get("tasks", []):
        results.append(dispatch(task))

    # 全handlerの実行結果を返す
    return results