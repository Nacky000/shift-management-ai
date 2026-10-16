import calendar
from datetime import date
from google.oauth2.service_account import Credentials
import gspread

# =========================
# Google Sheets設定
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SERVICE_ACCOUNT_FILE = "Config/service_account.json"

# スタッフ管理用Spreadsheet
USER_SPREADSHEET_NAME = "ShiftBot_Users"
USER_SHEET_NAME = "Users"


# =========================
# Google Sheets接続
# =========================

def get_client():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


# =========================
# スタッフ管理
# =========================

def get_users_sheet():
    """
    ShiftBot_Users の Users シートを取得する
    """

    client = get_client()

    spreadsheet = client.open(USER_SPREADSHEET_NAME)

    try:
        worksheet = spreadsheet.worksheet(USER_SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=USER_SHEET_NAME,
            rows=100,
            cols=4
        )

        worksheet.update(
            range_name="A1:D1",
            values=[
                ["user_id", "LINE表示名", "名前", "状態"]
            ]
        )

    return worksheet

def get_active_users():
    """
    状態が「有効」のスタッフだけ取得する
    """

    worksheet = get_users_sheet()

    records = worksheet.get_all_records()

    active_users = []

    for user in records:
        if user.get("状態") == "有効":
            active_users.append({
                "user_id": user.get("user_id"),
                "name": user.get("名前"),
                "line_name": user.get("LINE表示名")
            })

    return active_users


def create_monthly_spreadsheet(year, month):
    """
    月別のGoogle Spreadsheetを作成する
    """

    client = get_client()

    spreadsheet_name = f"ShiftBot_{year}_{month:02d}"

    try:
        spreadsheet = client.open(spreadsheet_name)
        print(f"{spreadsheet_name} は既に存在します。")

    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)
        print(f"{spreadsheet_name} を作成しました。")

    return spreadsheet


def get_monthly_worksheet(spreadsheet, year, month):
    """
    月別Spreadsheet内のシフト用Worksheetを取得する
    """

    sheet_name = f"{month}月シフト"

    try:
        worksheet = spreadsheet.worksheet(sheet_name)

    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=sheet_name,
            rows=100,
            cols=40
        )

    return worksheet


def create_date_headers(year, month):
    """
    月の日付と曜日を作成する
    """

    _, last_day = calendar.monthrange(year, month)

    dates = []
    weekdays = []

    weekday_names = ["月", "火", "水", "木", "金", "土", "日"]

    for day in range(1, last_day + 1):

        d = date(year, month, day)

        dates.append(f"{month}/{day}")
        weekdays.append(weekday_names[d.weekday()])

    return dates, weekdays

def create_staff_rows(worksheet):
    """
    有効なスタッフを3行目以降に配置する
    """

    users = get_active_users()

    staff_names = []

    for user in users:
        staff_names.append([user["name"]])

    if staff_names:
        worksheet.update(
            range_name=f"A3:A{2 + len(staff_names)}",
            values=staff_names
        )


def column_letter(number):
    """
    1 -> A
    2 -> B
    ...
    26 -> Z
    27 -> AA
    """

    result = ""

    while number > 0:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result

    return result


def create_monthly_template(year, month):
    """
    月別シフトSpreadsheetを作成し、
    日付・曜日・スタッフを自動生成する
    """

    # 月別Spreadsheet
    spreadsheet = create_monthly_spreadsheet(
        year,
        month
    )

    # 月別Worksheet
    worksheet = get_monthly_worksheet(
        spreadsheet,
        year,
        month
    )

    # 日付・曜日
    dates, weekdays = create_date_headers(
        year,
        month
    )

    # 最終列
    last_column = column_letter(len(dates) + 1)

    # 1行目：日付
    worksheet.update(
        range_name=f"A1:{last_column}1",
        values=[
            ["スタッフ"] + dates
        ]
    )

    # 2行目：曜日
    worksheet.update(
        range_name=f"A2:{last_column}2",
        values=[
            ["曜日"] + weekdays
        ]
    )

    # スタッフ
    create_staff_rows(worksheet)

    # 見やすくする
    worksheet.freeze_rows(2)
    worksheet.freeze_columns(1)

    print(
        f"{year}年{month}月のシフト表を作成しました。"
    )


###

def write_change(user_id, task):
    """シフト変更を書き込む"""
    sheet = get_default_sheet()
    sheet.append_row([
        user_id,
        "change",
        task.get("date"),
        task.get("old_start"),
        task.get("old_end"),
        task.get("new_start"),
        task.get("new_end"),
    ])


def write_absence(user_id, task):
    """欠勤情報を書き込む"""
    sheet = get_default_sheet()
    sheet.append_row([user_id, "absence", task.get("date"), task.get("reason", "")])


def write_late(user_id, task):
    """遅刻情報を書き込む"""
    sheet = get_default_sheet()
    sheet.append_row([
        user_id,
        "late",
        task.get("mode"),
        task.get("date"),
        task.get("arrival_time"),
        task.get("delay_minutes"),
        task.get("reason", ""),
    ])


def write_preference(user_id, task):
    """曜日希望を書き込む"""
    sheet = get_default_sheet()
    sheet.append_row([
        user_id,
        "preference",
        task.get("weekday"),
        task.get("start"),
        task.get("end"),
        task.get("available"),
        task.get("content", ""),
    ])


def write_memo(user_id, task):
    """メモを書き込む"""
    sheet = get_default_sheet()
    sheet.append_row([user_id, "memo", task.get("content", "")])


def read_question(user_id, task):
    """質問内容に応じてシフト情報などを取得する"""
    sheet = get_default_sheet()
    return sheet.get_all_records()


if __name__ == "__main__":
    create_monthly_template(2026, 10)