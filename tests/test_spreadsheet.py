from unittest.mock import Mock
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
