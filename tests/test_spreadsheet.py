from unittest.mock import Mock
import pytest
from Spreadsheet import spreadsheet


USER_ID = "test_user_001"
STAFF_NAME = "テスト"


def setup_fake_sheet(monkeypatch, existing_value=None):
    """Google Sheetsを呼び出さずにwrite_scheduleをテストする準備"""

    worksheet = Mock()

    # A列：1行目空欄，2行目見出し，3行目スタッフ名
    worksheet.col_values.return_value = ["", "スタッフ", STAFF_NAME]

    # 1行目：A列空欄，B列が10/28
    worksheet.row_values.return_value = ["", "10/28"]

    # B3セルの現在値（新規登録ならNone，更新なら既存値）
    fake_cell = Mock()
    fake_cell.value = existing_value
    worksheet.cell.return_value = fake_cell

    fake_spreadsheet = Mock()

    # 外部のGoogle Sheets接続をすべて置き換える
    monkeypatch.setattr(
        spreadsheet,
        "get_active_users",
        Mock(return_value=[
            {
                "user_id": USER_ID,
                "name": STAFF_NAME,
                "line_name": "テストユーザー",
            }
        ]),
    )

    monkeypatch.setattr(
        spreadsheet,
        "ensure_monthly_template",
        Mock(),
    )

    monkeypatch.setattr(
        spreadsheet,
        "get_monthly_spreadsheet",
        Mock(return_value=fake_spreadsheet),
    )

    monkeypatch.setattr(
        spreadsheet,
        "get_existing_monthly_worksheets",
        Mock(return_value={"シフト希望": worksheet}),
    )

    return worksheet


def test_write_schedule_writes_correct_cell(monkeypatch):
    """正しいスタッフ行・日付列にシフトを書き込む"""

    worksheet = setup_fake_sheet(monkeypatch)

    task = {
        "date": "2026-10-28",
        "start_time": "18:00",
        "end_time": "21:00",
    }

    result = spreadsheet.write_schedule(USER_ID, task)

    # 3行目、2列目（B3）に書き込まれる
    worksheet.update_cell.assert_called_once_with(3, 2, "18:00~21:00")

    # 新規登録なのでB3が新規登録用の色になる
    worksheet.format.assert_called_once_with(
        "B3",
        {
            "backgroundColor": {
                "red": 0.75,
                "green": 0.90,
                "blue": 0.75,
            }
        },
    )

    assert result == "10/28のシフト希望を登録しました"


def test_write_schedule_updates_existing_cell(monkeypatch):
    """登録済みのセルなら更新用の色になる"""

    worksheet = setup_fake_sheet(monkeypatch, existing_value="17:00~20:00")

    task = {
        "date": "2026-10-28",
        "start_time": "18:00",
        "end_time": "21:00",
    }

    spreadsheet.write_schedule(USER_ID, task)

    worksheet.update_cell.assert_called_once_with(3, 2, "18:00~21:00")

    # 更新時の色は黄色系
    worksheet.format.assert_called_once_with(
        "B3",
        {
            "backgroundColor": {
                "red": 1.0,
                "green": 0.95,
                "blue": 0.65,
            }
        },
    )


def test_write_schedule_rejects_missing_date(monkeypatch):
    """日付がない場合は書き込み前にエラーにする"""

    task = {
        "start_time": "18:00",
        "end_time": "21:00",
    }

    try:
        spreadsheet.write_schedule(USER_ID, task)
    except ValueError as exc:
        assert str(exc) == "日付が必要です"
    else:
        raise AssertionError("ValueErrorが発生するはずです")


# -----------------------------
# write_schedule() の異常系テスト
# -----------------------------

def test_write_schedule_rejects_missing_user(monkeypatch):
    """未登録・無効ユーザーはシフトを登録できない"""

    monkeypatch.setattr(
        spreadsheet,
        "get_active_users",
        Mock(return_value=[])
    )

    with pytest.raises(ValueError, match="ユーザーが登録されていない"):
        spreadsheet.write_schedule(
            USER_ID,
            {
                "date": "2026-11-12",
                "start_time": "18:00",
                "end_time": "22:00",
            }
        )


def test_write_schedule_rejects_missing_staff_row(monkeypatch):
    """シフト表にスタッフ名が存在しない場合はエラー"""

    worksheet = setup_fake_sheet(monkeypatch)

    worksheet.col_values.return_value = ["", "スタッフ", "別のスタッフ"]

    with pytest.raises(ValueError, match="シフト表にスタッフが見つかりません"):
        spreadsheet.write_schedule(
            USER_ID,
            {
                "date": "2026-11-12",
                "start_time": "18:00",
                "end_time": "22:00",
            }
        )


def test_write_schedule_rejects_missing_date_column(monkeypatch):
    """シフト表に対象日付の列が存在しない場合はエラー"""

    worksheet = setup_fake_sheet(monkeypatch)

    worksheet.row_values.return_value = ["", "11/10", "11/11"]

    with pytest.raises(ValueError, match="シフト表に日付が見つかりません"):
        spreadsheet.write_schedule(
            USER_ID,
            {
                "date": "2026-11-12",
                "start_time": "18:00",
                "end_time": "22:00",
            }
        )


def test_write_schedule_rejects_missing_time_and_memo():
    """開始・終了時刻も希望内容もない場合はエラー"""

    with pytest.raises(
        ValueError,
        match="開始時刻・終了時刻・希望内容のいずれかが必要です"
    ):
        spreadsheet.write_schedule(
            USER_ID,
            {
                "date": "2026-11-12",
                "start_time": None,
                "end_time": None,
                "memo": "",
            }
        )


# -----------------------------
# get_existing_monthly_worksheets() のテスト
# -----------------------------

def test_get_existing_monthly_worksheets_missing_sheet():
    """必要なシートが存在しない場合はエラー"""

    fake_spreadsheet = Mock()

    def fake_worksheet(name):
        if name == "シフト希望":
            raise spreadsheet.gspread.WorksheetNotFound(name)

        worksheet = Mock()
        worksheet.title = name
        return worksheet

    fake_spreadsheet.worksheet.side_effect = fake_worksheet

    with pytest.raises(ValueError, match="必要なシート"):
        spreadsheet.get_existing_monthly_worksheets(fake_spreadsheet)


# -----------------------------
# setup_application_sheet() のテスト
# -----------------------------

def test_setup_application_sheet_initializes_empty_sheet():
    """空のシフト申請シートにヘッダーを設定できる"""

    sheet = Mock()
    sheet.row_values.return_value = []

    spreadsheet.setup_application_sheet(sheet)

    sheet.update.assert_called_once_with(
        range_name="A1:P1",
        values=[spreadsheet.APPLICATION_HEADERS],
    )

    sheet.format.assert_called_once()
    sheet.freeze.assert_called_once_with(rows=1)


def test_setup_application_sheet_rejects_invalid_headers():
    """シフト申請シートのヘッダーが違う場合はエラー"""

    sheet = Mock()
    sheet.row_values.return_value = ["user_id", "名前", "間違った項目"]

    with pytest.raises(ValueError, match="ヘッダーが想定と異なります"):
        spreadsheet.setup_application_sheet(sheet)


# -----------------------------
# setup_attendance_sheet() のテスト
# -----------------------------

def test_setup_attendance_sheet_initializes_empty_sheet():
    """空の勤務連絡シートにヘッダーを設定できる"""

    sheet = Mock()
    sheet.row_values.return_value = []

    spreadsheet.setup_attendance_sheet(sheet)

    sheet.update.assert_called_once_with(
        range_name="A1:I1",
        values=[spreadsheet.ATTENDANCE_HEADERS],
    )

    sheet.format.assert_called_once()
    sheet.freeze_rows.assert_called_once_with(1)


def test_setup_attendance_sheet_rejects_invalid_headers():
    """勤務連絡シートのヘッダーが違う場合はエラー"""

    sheet = Mock()
    sheet.row_values.return_value = ["user_id", "名前", "間違った項目"]

    with pytest.raises(ValueError, match="ヘッダーが想定と異なります"):
        spreadsheet.setup_attendance_sheet(sheet)



def test_write_change_records_history_and_updates_shift(monkeypatch):
    """変更履歴を残し、シフト希望も更新する"""

    application_sheet = Mock()
    shift_sheet = Mock()

    shift_sheet.col_values.return_value = [
        "",
        "スタッフ",
        STAFF_NAME,
    ]
    shift_sheet.row_values.return_value = [
        "",
        "11/12",
    ]

    monkeypatch.setattr(
        spreadsheet,
        "get_target_month",
        Mock(return_value=(2026, 11)),
    )

    monkeypatch.setattr(
        spreadsheet,
        "get_monthly_sheet",
        Mock(side_effect=lambda y, m, name: {
            "シフト申請": application_sheet,
            "シフト希望": shift_sheet,
        }[name]),
    )

    monkeypatch.setattr(
        spreadsheet,
        "setup_application_sheet",
        Mock(),
    )

    monkeypatch.setattr(
        spreadsheet,
        "get_staff_name",
        Mock(return_value=STAFF_NAME),
    )

    task = {
        "date": "2026-11-12",
        "old_start_time": "18:00",
        "old_end_time": "22:00",
        "new_start_time": "19:00",
        "new_end_time": "23:00",
        "reason": "予定変更",
        "memo": "授業のため",
    }

    result = spreadsheet.write_change(USER_ID, task)

    # 申請履歴が記録される
    application_sheet.append_row.assert_called_once()

    saved_data = application_sheet.append_row.call_args.args[0]

    assert saved_data[0] == USER_ID
    assert saved_data[2] == "シフト変更"
    assert saved_data[5] == "18:00"
    assert saved_data[6] == "22:00"
    assert saved_data[7] == "19:00"
    assert saved_data[8] == "23:00"

    # シフト希望が更新される
    shift_sheet.update_cell.assert_called_once_with(
        3, 2, "19:00~23:00（授業のため）"
    )

    assert result == (
        "シフト変更を記録し、シフト希望を更新しました。"
    )
