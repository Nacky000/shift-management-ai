# change_handler.py

from Spreadsheet.spreadsheet import write_change

def change_handler(user_id,task):
    """
    シフト変更の処理
    """

    cleaned = {
        "date": task.get("date"),
        "old_start": task.get("old_start"),
        "old_end": task.get("old_end"),
        "new_start": task.get("new_start"),
        "new_end": task.get("new_end")
    }

    # user_id と 整形済みデータ(cleaned) をスプレッドシートへ渡す
    write_change(user_id, cleaned)

    # LINE側に返す確認メッセージ
    date_str = cleaned["date"] if cleaned["date"] else "指定日"
    return f"【シフト変更】\n{date_str}のシフト変更申請（{cleaned['old_start']}➔{cleaned['new_start']}など）を受け付けました．"