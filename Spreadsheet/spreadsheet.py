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

# Google Drive上の保存先フォルダID
DRIVE_FOLDER_ID = "1L5odcJ7WSSM776cEX0FSySGxAfmYCNb2"

# スタッフ管理用Spreadsheet
USER_SPREADSHEET_NAME = "ShiftBot_Users"
USER_SHEET_NAME = "Users"

# 月別Spreadsheetのシート名
SHIFT_SHEET_NAMES = [
    "シフト希望",
    "シフト調整",
    "確定シフト",
]


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


def setup_user_status_dropdown():
    """Usersシートの状態列をプルダウン選択式にする。"""
    worksheet = get_users_sheet()

    worksheet.spreadsheet.batch_update({
        "requests": [
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 3,
                        "endColumnIndex": 4,
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [
                                {"userEnteredValue": "確認中"},
                                {"userEnteredValue": "有効"},
                                {"userEnteredValue": "無効"},
                            ],
                        },
                        "showCustomUi": True,
                        "strict": True,
                        "inputMessage": "スタッフの状態を選択してください",
                    },
                }
            }
        ]
    })



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


def register_user(user_id, line_name):
    """
    未登録のLINEユーザーを確認中として登録する。
    登録済みユーザーは重複登録しない。
    """

    worksheet = get_users_sheet()
    records = worksheet.get_all_records()

    for row_number, user in enumerate(records, start=2):
        if str(user.get("user_id", "")).strip() == str(user_id).strip():
            return False  # 登録済み

    worksheet.append_row([
        user_id,
        line_name,
        "",
        "確認中",
    ])

    return True

# =========================
# スタッフのLINE連携
# =========================


def get_user_status(user_id):
    """LINEユーザーIDから登録状態を取得する。未登録ならNone。"""
    worksheet = get_users_sheet()
    records = worksheet.get_all_records()

    for user in records:
        if str(user.get("user_id", "")).strip() == str(user_id).strip():
            return str(user.get("状態", "")).strip()

    return None



# =========================
# シート管理
# =========================



def create_monthly_spreadsheet(year, month):
    """
    月別のGoogle Spreadsheetを取得する。
    存在しなければ指定フォルダに作成する。
    """

    client = get_client()
    spreadsheet_name = f"ShiftBot_{year}_{month:02d}"

    try:
        spreadsheet = client.open(spreadsheet_name)
        print(f"{spreadsheet_name} は既に存在します。")

    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(
            spreadsheet_name,
            folder_id=DRIVE_FOLDER_ID
        )
        print(f"{spreadsheet_name} を作成しました。")

    return spreadsheet



def get_monthly_worksheets(spreadsheet):
    """
    月別Spreadsheetの3シートを取得する。
    存在しないシートは新規作成する。
    """

    worksheets = {}

    for sheet_name in SHIFT_SHEET_NAMES:
        try:
            worksheet = spreadsheet.worksheet(sheet_name)

        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=sheet_name,
                rows=100,
                cols=40
            )

        worksheets[sheet_name] = worksheet

    return worksheets


def get_existing_monthly_worksheets(spreadsheet):
    """
    既存の月別Spreadsheetから3シートを取得する。
    不足しているシートがあっても自動作成しない。
    """

    worksheets = {}

    for sheet_name in SHIFT_SHEET_NAMES:
        try:
            worksheets[sheet_name] = spreadsheet.worksheet(sheet_name)

        except gspread.WorksheetNotFound:
            raise ValueError(
                f"必要なシート「{sheet_name}」がありません。"
                "月別シフト表の構成を確認してください。"
            )

    return worksheets




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
    月別Spreadsheetを作成し、
    3シートの初期レイアウトを準備する。
    """

    spreadsheet = create_monthly_spreadsheet(
        year,
        month
    )

    worksheets = get_monthly_worksheets(spreadsheet)

    dates, weekdays = create_date_headers(year, month)

    last_column = column_letter(len(dates) + 1)

    users = get_active_users()
    staff_names = [
        user["name"]
        for user in users
        if user.get("name")
    ]

    for sheet_name, worksheet in worksheets.items():

        # 1行目：日付
        worksheet.update(
            range_name=f"A1:{last_column}1",
            values=[["スタッフ"] + dates]
        )

        # 2行目：曜日
        worksheet.update(
            range_name=f"A2:{last_column}2",
            values=[["曜日"] + weekdays]
        )

        # 3行目以降：スタッフ名
        if staff_names:
            worksheet.update(
                range_name=f"A3:A{2 + len(staff_names)}",
                values=[[name] for name in staff_names]
            )

        worksheet.freeze_rows(2)
        worksheet.freeze_columns(1)

    print(
        f"{year}年{month}月のシフト表を準備しました"
    )


def get_monthly_spreadsheet(year, month):
    """既存の月別スプレッドシートを取得する。"""
    client = get_client()
    spreadsheet_name = f"ShiftBot_{year}_{month:02d}"

    try:
        return client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        raise FileNotFoundError(
            f"{spreadsheet_name} が見つかりません。"
            "先に月別スプレッドシートを作成してください。"
        )


def ensure_monthly_template(year, month):
    """
    既存の月別シフト表を確認し、
    日付・曜日・スタッフ名が不足していれば補完する。
    ファイルやシートは新規作成しない。
    """

    spreadsheet = get_monthly_spreadsheet(year, month)
    worksheets = get_existing_monthly_worksheets(spreadsheet)

    dates, weekdays = create_date_headers(year, month)
    last_column = column_letter(len(dates) + 1)

    users = get_active_users()
    staff_names = [
        user["name"]
        for user in users
        if user.get("name")
    ]

    for worksheet in worksheets.values():
        # 日付が未設定の場合だけ補完
        headers = worksheet.row_values(1)
        expected_dates = [""] + dates

        if headers[:len(expected_dates)] != expected_dates:
            worksheet.update(
                range_name=f"A1:{last_column}1",
                values=[expected_dates]
            )

        # 曜日が未設定の場合だけ補完
        weekday_row = worksheet.row_values(2)
        expected_weekdays = ["スタッフ"] + weekdays

        if weekday_row[:len(expected_weekdays)] != expected_weekdays:
            worksheet.update(
                range_name=f"A2:{last_column}2",
                values=[expected_weekdays]
            )

        # 既存のスタッフ名を保持し、不足分だけ追加
        existing_names = worksheet.col_values(1)
        existing_names = existing_names[2:]

        missing_names = [
            name for name in staff_names
            if name not in existing_names
        ]

        if missing_names:
            start_row = max(3, len(existing_names) + 3)
            end_row = start_row + len(missing_names) - 1

            worksheet.update(
                range_name=f"A{start_row}:A{end_row}",
                values=[[name] for name in missing_names]
            )

        worksheet.freeze(rows=2, cols=1)
    

def write_schedule(user_id, task):
    """
    LINEから受け取ったシフト希望を
    対象月の「シフト希望」シートに保存する

    taskの形式:
    {
        "date": "2026-10-25",
        "start_time": "18:00",
        "end_time": "22:00"
    }
    """
    

    # 日付・勤務時間を取得
    date_value = task.get("date")
    start_time = task.get("start_time") or task.get("start")
    end_time = task.get("end_time") or task.get("end")

    if not date_value or not start_time or not end_time:
        raise ValueError(
            "日付・開始時刻・終了時刻が必要です"
        )

    if isinstance(date_value, date):
        shift_date = date_value
    else:
        shift_date = date.fromisoformat(str(date_value))

    year = shift_date.year
    month = shift_date.month
    date_header = f"{month}/{shift_date.day}"

    # ユーザーIDから有効なスタッフを特定
    users = get_active_users()

    user = next(
        (
            u for u in users
            if str(u["user_id"]).strip() == str(user_id).strip()
        ),
        None
    )

    if not user or not user.get("name"):
        raise ValueError(
            "ユーザーが登録されていないか、有効ではありません"
        )

    staff_name = user["name"]

    # 既存のシフト表を確認し、不足する見出しなどを補完
    ensure_monthly_template(year, month)

    spreadsheet = get_monthly_spreadsheet(year, month)
    worksheets = get_existing_monthly_worksheets(spreadsheet)
    worksheet = worksheets["シフト希望"]

    # スタッフの行を探す（A列、3行目以降）
    staff_names = worksheet.col_values(1)

    staff_row = next(
        (
            row
            for row, name in enumerate(staff_names, start=1)
            if row >= 3 and name.strip() == staff_name
        ),
        None
    )

    if staff_row is None:
        raise ValueError(
            f"シフト表にスタッフが見つかりません: {staff_name}"
        )

    # 日付の列を探す（1行目）
    headers = worksheet.row_values(1)

    date_column = next(
        (
            col
            for col, value in enumerate(headers, start=1)
            if col >= 2 and value == date_header
        ),
        None
    )

    if date_column is None:
        raise ValueError(
            f"シフト表に日付が見つかりません: {date_header}"
        )

    # 初回登録か更新かを判定
    cell = f"{column_letter(date_column)}{staff_row}"
    old_value = worksheet.cell(staff_row, date_column).value

    if old_value:
        color = {
            "red": 1.0,
            "green": 0.95,
            "blue": 0.65
        }
        status = "更新"
    else:
        color = {
            "red": 0.75,
            "green": 0.90,
            "blue": 0.75
        }
        status = "新規"

    # 書き込みと色付け
    worksheet.update_cell(
        staff_row,
        date_column,
        f"{start_time}~{end_time}"
    )

    worksheet.format(
        cell,
        {"backgroundColor": color}
    )

    print(
        f"{status}: {staff_name} / "
        f"{shift_date} / {start_time}~{end_time}"
    )

    return f"{shift_date.month}/{shift_date.day}のシフト希望を登録しました"


# =========================
# シフト管理
# =========================


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
