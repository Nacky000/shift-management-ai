# memo_handler.py

from Spreadsheet.spreadsheet import write_memo

def memo_handler(task):
    """
    メモの処理
    """

    cleaned = {
        "content": task.get("content", "")
    }

    return write_memo(cleaned)