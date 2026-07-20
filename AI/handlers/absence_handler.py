# absence_handler.py

from Spreadsheet.spreadsheet import write_absence

def absence_handler(user_id,task):
    """
    欠席連絡の処理
    """

    cleaned = {
        "date": task.get("date"),
        "reason": task.get("reason", "")
    }
   
    # user_id と 整形済みデータ(cleaned) をスプレッドシートへ渡す
    write_absence(user_id, cleaned)

    # LINE側に返す確認メッセージ
    date_str = cleaned["date"] if cleaned["date"] else "指定日"
    return f"【欠勤連絡】\n{date_str}の欠勤連絡を承りました．店長へ通知します．"