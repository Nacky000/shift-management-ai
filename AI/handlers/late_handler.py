# late_handler.py

from Spreadsheet.spreadsheet import write_late

def late_handler(task):
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

    return write_late(cleaned)