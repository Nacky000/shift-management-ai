# dispatcher.py 

from AI.handlers.schedule_handler import schedule_handler
from AI.handlers.change_handler import change_handler
from AI.handlers.absence_handler import absence_handler
from AI.handlers.late_handler import late_handler
from AI.handlers.preference_handler import preference_handler
from AI.handlers.question_handler import question_handler
from AI.handlers.memo_handler import memo_handler
from AI.handlers.other_handler import other_handler

handlers = {
    "schedule": schedule_handler,
    "change": change_handler,
    "absence": absence_handler,
    "late": late_handler,
    "preference": preference_handler,
    "question": question_handler,
    "memo": memo_handler,
    "other": other_handler
}


def dispatch(task):

    task_type = task.get("type")

    handler = handlers.get(task_type, other_handler)

    return handler(task)