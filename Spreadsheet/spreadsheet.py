# spreadsheet.py

def write_schedule(task):
    """シフト提出を書き込む"""
    print("schedule", task)


def write_change(task):
    """シフト変更を書き込む"""
    print("change", task)


def write_absence(task):
    """欠勤情報を書き込む"""
    print("absence", task)


def write_late(task):
    """遅刻情報を書き込む"""
    print("late", task)


def write_preference(task):
    """曜日希望を書き込む"""
    print("preference", task)


def read_schedule(task):
    """シフトを取得する"""
    print("read schedule", task)
    return None