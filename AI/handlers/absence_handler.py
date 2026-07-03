# absence_handler.py

from Spreadsheet.spreadsheet import write_absence

def absence_handler(task):
    """
    欠席連絡の処理
    """

    cleaned = {
        "date": task.get("date"),
        "reason": task.get("reason", "")
    }
   
    return write_absence(task)