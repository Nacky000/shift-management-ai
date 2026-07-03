# change_handler.py

from Spreadsheet.spreadsheet import write_change

def change_handler(task):
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

    return write_change(cleaned)