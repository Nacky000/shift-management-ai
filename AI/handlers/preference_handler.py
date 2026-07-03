# preference_handler.py

from Spreadsheet.spreadsheet import write_preference

def preference_handler(task):
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

    return write_preference(cleaned)