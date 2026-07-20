# late_handler.py

from Spreadsheet.spreadsheet import write_late

def late_handler(user_id,task):
    """
    遅刻連絡の処理
    """

    cleaned = {
        "mode": task.get("mode"),
        "date": task.get("date"),
        "arrival_time": task.get("arrival_time"),
        "delay_minutes": task.get("delay_minutes"),
        "reason": task.get("reason", "")
    }

    # user_id と 整形済みデータ(cleaned) をスプレッドシートへ渡す
    write_late(user_id, cleaned)

    # LINE側に返す確認メッセージ
    date_str = cleaned["date"] if cleaned["date"] else "指定日"
    return f"【遅刻連絡】\n{date_str}の遅刻連絡（{cleaned['arrival_time'] or ''}頃到着予定）を承りました．店長へ通知します．"