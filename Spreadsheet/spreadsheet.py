import calendar
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# ユーザーIDとスタッフ名の紐付け辞書
# ※ 新しい人が増えたらここに追加します
# ==========================================
USER_MAP = {
    "U27270693436a29fa7e5a884e4663dd99": "植木",
    # "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx": "田中",  # 例
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_NAME = "ShiftBot"


def get_client():
    """gspreadのクライアントを取得する"""
    credentials = Credentials.from_service_account_file(
        "Config/service_account.json", scopes=SCOPES
    )
    return gspread.authorize(credentials)


def get_or_create_month_sheet(client, year, month):
    """月ごとのシートを取得、なければカレンダーの原型を自動作成する"""
    sh = client.open(SHEET_NAME)
    sheet_name = f"{year}年{month:02d}月"

    try:
        ws = sh.worksheet(sheet_name)
        return ws
    except Exception:
        # シートがない場合は新規作成
        ws = sh.add_worksheet(title=sheet_name, rows="100", cols="20")

        # 1列目に日付の枠を自動生成 (A1は空白、A2から1日、2日...)
        _, last_day = calendar.monthrange(year, month)
        headers = [["日付 / スタッフ"]] + [
            [f"{day}日"] for day in range(1, last_day + 1)
        ]
        ws.update(range_name="A1:A" + str(last_day + 1), values=headers)

        return ws


def write_schedule(user_id, shifts):
    """シフト提出を月ごとのカレンダー風クロス集計表に書き込む"""
    client = get_client()

    # 1. ユーザーIDから名前を変換（登録がなければIDの先頭8文字）
    staff_name = USER_MAP.get(user_id, user_id[:8])

    for s in shifts:
        # 日付文字列 (例: "2026-08-06") から数値を抽出
        try:
            dt = datetime.strptime(s["date"], "%Y-%m-%d")
            year, month, day = dt.year, dt.month, dt.day
        except Exception as e:
            print(f"日付パースエラー: {e}")
            continue

        # 2. 対象月のシートを取得（なければ自動生成）
        ws = get_or_create_month_sheet(client, year, month)

        # 3. 横軸（1行目）からスタッフ名を探す
        first_row = ws.row_values(1)
        if staff_name in first_row:
            col_idx = first_row.index(staff_name) + 1
        else:
            # 見つからなければ、右端の空いている列にスタッフ名を追加
            col_idx = len(first_row) + 1
            ws.update_cell(1, col_idx, staff_name)

        # 4. 縦軸（日付の行）のインデックスを計算
        # A2セルが1日なので、行番号は「日付 + 1」
        row_idx = day + 1

        # 5. シフト時間（例: "15:00~20:00"）を書き込み
        shift_time = f"{s['start']}~{s['end']}"
        ws.update_cell(row_idx, col_idx, shift_time)
        print(
            f"【カレンダー反映】{year}年{month}月シート: {day}日 の {staff_name} へ 「{shift_time}」を書き込みました。"
        )


def get_default_sheet():
    """従来のログ保存用のシート(sheet1)を取得する"""
    client = get_client()
    return client.open(SHEET_NAME).sheet1


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