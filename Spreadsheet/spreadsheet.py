import calendar
from datetime import date, datetime
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
    "シフト申請",
    "勤務連絡",
]

# 日付・曜日・スタッフの表を使うシート
GRID_SHEET_NAMES = [
    "シフト希望",
    "シフト調整",
    "確定シフト",
]

# シフト変更・固定希望を記録するシート
APPLICATION_HEADERS = [
    "user_id",
    "スタッフ名",
    "申請種別",
    "対象日",
    "曜日",
    "変更前開始",
    "変更前終了",
    "変更後開始",
    "変更後終了",
    "希望開始",
    "希望終了",
    "勤務可能",
    "補足",
    "登録日時",
    "確認済み",
]

# 欠勤・遅刻などを記録するシート
ATTENDANCE_HEADERS = [
    "user_id",
    "スタッフ名",
    "連絡種別",
    "対象日",
    "開始予定時刻",
    "遅延時間（分）",
    "理由・補足",
    "登録日時",
    "確認済み",
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

def setup_application_sheet(sheet):
    """シフト申請シートの見出しと確認チェックボックスを設定する。"""

    headers = sheet.row_values(1)

    if not headers:
        sheet.update(
            range_name="A1:O1",
            values=[APPLICATION_HEADERS],
        )
    elif headers[:len(APPLICATION_HEADERS)] != APPLICATION_HEADERS:
        raise ValueError(
            "シフト申請シートのヘッダーが想定と異なります。"
            "既存データを確認してから修正してください。"
        )

    # O列：確認済みチェックボックス
    sheet.spreadsheet.batch_update({
        "requests": [
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 14,
                        "endColumnIndex": 15,
                    },
                    "rule": {
                        "condition": {
                            "type": "BOOLEAN",
                        },
                        "showCustomUi": True,
                        "strict": True,
                    },
                }
            }
        ]
    })

    sheet.format(
        "A1:O1",
        {
            "backgroundColor": {
                "red": 0.25,
                "green": 0.30,
                "blue": 0.35,
            },
            "textFormat": {
                "bold": True,
                "foregroundColor": {
                    "red": 1,
                    "green": 1,
                    "blue": 1,
                },
            },
        },
    )

    sheet.freeze(rows=1)


def create_monthly_template(year, month):
    """
    月別Spreadsheetを取得または作成し、
    3つのシフト表と2つの記録シートを初期化する。
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

        sheet_name = worksheet.title

        if sheet_name in GRID_SHEET_NAMES:

            # 1行目：A列は空欄、B列以降に日付
            worksheet.update(
                range_name=f"A1:{last_column}1",
                values=[[""] + dates]
            )

            # 2行目：A列にスタッフ、B列以降に曜日
            worksheet.update(
                range_name=f"A2:{last_column}2",
                values=[["スタッフ"] + weekdays]
            )

            # 3行目以降：スタッフ名
            if staff_names:
                worksheet.update(
                    range_name=f"A3:A{2 + len(staff_names)}",
                    values=[[name] for name in staff_names]
                )

            worksheet.freeze_rows(2)
            worksheet.freeze_columns(1)

        elif sheet_name == "シフト申請":
            setup_application_sheet(worksheet)

        elif sheet_name == "勤務連絡":
            setup_attendance_sheet(worksheet)

    


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
        sheet_name = worksheet.title

        if sheet_name in GRID_SHEET_NAMES:
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

        elif sheet_name == "シフト申請":
            # 空のシートなら初期化する
            if not worksheet.get_all_values():
                setup_application_sheet(worksheet)

        elif sheet_name == "勤務連絡":
            # 空のシートなら初期化する
            if not worksheet.get_all_values():
                setup_attendance_sheet(worksheet)
    

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
    memo = task.get("memo") or ""

    if not date_value:
        raise ValueError("日付が必要です")

    if not start_time and not end_time and not memo:    
        raise ValueError(
            "開始時刻・終了時刻・希望内容のいずれかが必要です"
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

    # 書き込み用の文字列を作成
    if start_time and end_time:
        shift_text = f"{start_time}~{end_time}"
    elif start_time:
        shift_text = f"{start_time}~未定"
    elif end_time:
        shift_text = f"未定~{end_time}"
    else:
        shift_text = memo or "時間未定"

    # 希望内容も記録する
    if memo and memo not in shift_text:
        shift_text += f"（{memo}）"

    # シフト希望を書き込み
    worksheet.update_cell(
        staff_row,
        date_column,
        shift_text
    )

    worksheet.format(
        cell,
        {"backgroundColor": color}
    )

    print(
        f"{status}: {staff_name} / "
        f"{shift_date} / {shift_text}"
    )

    return f"{shift_date.month}/{shift_date.day}のシフト希望を登録しました"


# =========================
# シフト管理
# =========================

def get_shift(user_id, date_value):
    """
    指定ユーザーの「シフト希望」シートから、
    指定日の登録済みシフトを取得する。

    Returns
    -------
    dict:
        {"start": "18:00", "end": "22:00"}
    シフトが未登録の場合は None。
    """
    # 日付を正規化
    if isinstance(date_value, date):
        shift_date = date_value
    else:
        shift_date = date.fromisoformat(str(date_value))

    year = shift_date.year
    month = shift_date.month
    date_header = f"{month}/{shift_date.day}"

    # ユーザーIDからスタッフを特定
    users = get_active_users()

    user = next(
        (
            u for u in users
            if str(u["user_id"]).strip() == str(user_id).strip()
        ),
        None,
    )

    if not user or not user.get("name"):
        return None

    staff_name = user["name"]

    # 対象月の「シフト希望」シートを取得
    try:
        spreadsheet = get_monthly_spreadsheet(year, month)
        worksheets = get_existing_monthly_worksheets(spreadsheet)
        worksheet = worksheets["シフト希望"]
    except FileNotFoundError:
        return None

    # スタッフの行を探す
    staff_names = worksheet.col_values(1)

    staff_row = next(
        (
            row
            for row, name in enumerate(staff_names, start=1)
            if row >= 3 and name.strip() == staff_name
        ),
        None,
    )

    if staff_row is None:
        return None

    # 日付の列を探す
    headers = worksheet.row_values(1)

    date_column = next(
        (
            col
            for col, value in enumerate(headers, start=1)
            if col >= 2 and value == date_header
        ),
        None,
    )

    if date_column is None:
        return None

    # 登録済みの希望時間を取得
    value = worksheet.cell(staff_row, date_column).value

    if not value:
        return None

    # 「19:00~未定（19時以降ならいつでも）」などから
    # 時間部分だけを取り出す
    time_text = value.split("（", 1)[0].split("(", 1)[0].strip()

    if "~" not in time_text:
        return None

    start, end = time_text.split("~", 1)

    start = start.strip()
    end = end.strip()

    # 「未定」は None に統一
    if start == "未定":
        start = None

    if end == "未定":
        end = None

    return {
        "start": start or None,
        "end": end or None,
    }

def get_target_month(task):
    """taskの日付から対象年月を取得する。"""
    date_value = task.get("date")

    if not date_value:
        raise ValueError("対象日が指定されていません。")

    if isinstance(date_value, date):
        target_date = date_value
    else:
        target_date = date.fromisoformat(str(date_value))

    return target_date.year, target_date.month



def get_monthly_sheet(year, month, sheet_name):
    """
    指定した月のスプレッドシートから、
    指定されたシートを取得する。
    """
    spreadsheet = get_monthly_spreadsheet(year, month)

    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        raise ValueError(
            f"必要なシート「{sheet_name}」がありません。"
            "先に月別シフト表を作成してください。"
        )
    

def write_change(user_id, task):
    """シフト変更をシフト申請シートに記録する。"""

    year, month = get_target_month(task)
    sheet = get_monthly_sheet(year, month, "シフト申請")

    setup_application_sheet(sheet)
    staff_name = get_staff_name(user_id)

    sheet.append_row([
        user_id,
        staff_name,
        "シフト変更",
        task.get("date") or "",
        "",
        task.get("old_start") or "",
        task.get("old_end") or "",
        task.get("new_start") or "",
        task.get("new_end") or "",
        "",
        "",
        "",
        task.get("reason") or "",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        False,
    ])

    return "シフト変更申請を記録しました。"



# =========================
# 勤務連絡
# =========================


# =========================
# 勤務連絡
# =========================

ATTENDANCE_HEADERS = [
    "user_id",
    "スタッフ名",
    "連絡種別",
    "対象日",
    "開始予定時刻",
    "遅延時間（分）",
    "理由・補足",
    "登録日時",
    "確認済み",
]

def get_staff_name(user_id):
    """LINEユーザーIDからスタッフ名を取得する。"""
    users = get_active_users()

    user = next(
        (
            u for u in users
            if str(u.get("user_id", "")).strip()
            == str(user_id).strip()
        ),
        None,
    )

    if not user or not user.get("name"):
        raise ValueError(
            "スタッフが未登録、または有効ではありません。"
        )

    return user["name"]


def setup_attendance_sheet(sheet):
    """勤務連絡シートのヘッダーと確認チェックボックスを設定する。"""

    headers = sheet.row_values(1)

    if not headers:
        sheet.update(
            range_name="A1:I1",
            values=[ATTENDANCE_HEADERS],
        )
    elif headers[:len(ATTENDANCE_HEADERS)] != ATTENDANCE_HEADERS:
        raise ValueError(
            "勤務連絡シートのヘッダーが想定と異なります。"
            "既存データを確認してから修正してください。"
        )

    # I列をチェックボックスにする
    sheet.spreadsheet.batch_update({
        "requests": [
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 8,
                        "endColumnIndex": 9,
                    },
                    "rule": {
                        "condition": {
                            "type": "BOOLEAN",
                        },
                        "showCustomUi": True,
                        "strict": True,
                    },
                }
            }
        ]
    })

    # ヘッダーを見やすくする
    sheet.format(
        "A1:I1",
        {
            "backgroundColor": {
                "red": 0.25,
                "green": 0.30,
                "blue": 0.35,
            },
            "textFormat": {
                "bold": True,
                "foregroundColor": {
                    "red": 1,
                    "green": 1,
                    "blue": 1,
                },
            },
        },
    )

    sheet.freeze_rows(1)


def write_attendance(user_id, task, contact_type):
    """欠勤・遅刻などの勤務連絡を共通形式で保存する。"""

    year, month = get_target_month(task)
    sheet = get_monthly_sheet(year, month, "勤務連絡")

    setup_attendance_sheet(sheet)

    staff_name = get_staff_name(user_id)

    # 追加する行番号を取得
    row_number = len(sheet.get_all_values()) + 1

    sheet.append_row([
        user_id,
        staff_name,
        contact_type,
        str(task.get("date")),
        task.get("arrival_time") or "",
        task.get("delay_minutes") or "",
        task.get("reason") or "",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        False,  # 確認済みチェックボックス：未確認
    ])

    # 欠勤は薄い赤、遅刻は薄い黄色
    if contact_type == "欠勤":
        color = {
            "red": 1.0,
            "green": 0.82,
            "blue": 0.82,
        }
    elif contact_type == "遅刻":
        color = {
            "red": 1.0,
            "green": 0.95,
            "blue": 0.70,
        }
    else:
        color = {
            "red": 0.90,
            "green": 0.90,
            "blue": 0.90,
        }

    # 連絡の行全体を色付け
    sheet.format(
        f"A{row_number}:I{row_number}",
        {"backgroundColor": color},
    )

    return row_number


def write_absence(user_id, task):
    """欠勤連絡を書き込む。"""
    return write_attendance(user_id, task, "欠勤")


def write_late(user_id, task):
    """遅刻連絡を書き込む。"""
    return write_attendance(user_id, task, "遅刻")



def write_preference(user_id, task):
    """固定希望をシフト申請シートに記録する。"""

    now = datetime.now()

    year = int(task.get("year") or now.year)
    month = int(task.get("month") or now.month)

    sheet = get_monthly_sheet(
        year,
        month,
        "シフト申請",
    )

    setup_application_sheet(sheet)
    staff_name = get_staff_name(user_id)

    sheet.append_row([
        user_id,
        staff_name,
        "固定希望",
        "",
        task.get("weekday") or "",
        "",
        "",
        "",
        "",
        task.get("start") or "",
        task.get("end") or "",
        task.get("available") or "",
        task.get("content") or "",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        False,
    ])

    return "固定希望を記録しました。"


# def write_memo(user_id, task):
#     """メモを書き込む"""
#     sheet = get_monthly_sheet(
#         int(year),
#         int(month),
#         ""
#     )
#     sheet.append_row([user_id, "memo", task.get("content", "")])


# def read_question(user_id, task):
#     """質問内容に応じてシフト情報などを取得する"""
#     sheet = get_monthly_sheet(
#         int(year),
#         int(month),
#         "シフト申請"
#     )
#     return sheet.get_all_records()
