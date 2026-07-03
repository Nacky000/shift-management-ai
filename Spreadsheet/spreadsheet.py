# spreadsheet.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_schedule(shifts):
    # shifts = cleaned list
    """シフト提出を書き込む"""
    print("schedule", shifts)


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


def read_question(task):
    """質問内容に応じてシフト情報などを取得する"""
    print("question", task)
    return None