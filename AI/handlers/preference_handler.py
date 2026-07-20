# preference_handler.py

from Spreadsheet.spreadsheet import write_preference

def preference_handler(user_id,task):
    """
    曜日ごとの希望提出の処理
    """

    cleaned = {
        "weekday": task.get("weekday"),
        "start": task.get("start"),
        "end": task.get("end"),
        "available": task.get("available"),
        "content": task.get("content", "")
    }

    # user_id と 整形済みデータ(cleaned) をスプレッドシートへ渡す
    write_preference(user_id, cleaned)

    # LINE側に返す確認メッセージ
    weekday_str = cleaned["weekday"] if cleaned["weekday"] else "指定の曜日"
    return f"【固定希望】\n{weekday_str}曜日のシフト希望・条件を登録しました．"