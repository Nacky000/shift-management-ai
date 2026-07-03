# spreadsheet.py
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "ShiftBot"

def get_sheet():
    credentials = Credentials.from_service_account_file(
        "Config/service_account.json",
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)
    return client.open("ShiftBot").sheet1


def write_schedule(shifts):
    # shifts = cleaned list
    """シフト提出を書き込む"""
    sheet = get_sheet()

    for s in shifts:
        sheet.append_row([
            "schedule",
            s["date"],
            s["start"],
            s["end"],
            s.get("memo", "")
        ])

def write_change(task):
    """シフト変更を書き込む"""
    sheet = get_sheet()

    sheet.append_row([
        "change",
        task.get("date"),
        task.get("old_start"),
        task.get("old_end"),
        task.get("new_start"),
        task.get("new_end")
    ])


def write_absence(task):
    """欠勤情報を書き込む"""
    sheet = get_sheet()

    sheet.append_row([
        "absence",
        task.get("date"),
        task.get("reason", "")
    ])


def write_late(task):
    """遅刻情報を書き込む"""
    sheet = get_sheet()

    sheet.append_row([
        "late",
        task.get("mode"),
        task.get("date"),
        task.get("arrival_time"),
        task.get("delay_minutes"),
        task.get("reason", "")
    ])


def write_preference(task):
    """曜日希望を書き込む"""
    sheet = get_sheet()

    sheet.append_row([
        "preference",
        task.get("weekday"),
        task.get("start"),
        task.get("end"),
        task.get("available"),
        task.get("content", "")
    ])


def write_memo(task):
    """メモを書き込む"""
    sheet = get_sheet()

    sheet.append_row([
        "memo",
        task.get("content", "")
    ])


def read_question(task):
    """質問内容に応じてシフト情報などを取得する"""
    sheet = get_sheet()

    # 今はダミー
    return sheet.get_all_records()