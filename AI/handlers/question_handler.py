# question_handler.py

from Spreadsheet.spreadsheet import read_question

def question_handler(task):

    cleaned = {
        "question_type": task.get("question_type"),
        "target": task.get("target"),
        "date": task.get("date"),
        "content": task.get("content", "")
    }

    return read_question(cleaned)