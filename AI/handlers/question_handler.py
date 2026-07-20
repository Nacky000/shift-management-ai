# question_handler.py

from Spreadsheet.spreadsheet import read_question

def question_handler(user_id,task):

    cleaned = {
        "question_type": task.get("question_type"),
        "target": task.get("target"),
        "date": task.get("date"),
        "content": task.get("content", "")
    }

    # データを読み出す（現在はダミーデータが返る状態）
    records = read_question(user_id, cleaned)

    # LINE側に返す確認メッセージ
    date_str = cleaned["date"] if cleaned["date"] else "指定日"
    return f"【シフト確認】\n{date_str}のシフト状況についての質問を受け付けました．現在シートから情報を確認しています．"