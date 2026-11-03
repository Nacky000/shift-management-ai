from unittest.mock import Mock

from AI.handlers import absence_handler as absence_module
from AI.handlers import late_handler as late_module


USER_ID = "test_user_001"


def test_absence_handler_writes_correct_data(monkeypatch):
    """欠勤連絡の内容を正しく保存関数に渡す"""

    mock_write = Mock()
    monkeypatch.setattr(absence_module, "write_absence", mock_write)

    task = {
        "date": "2026-11-12",
        "reason": "体調不良",
    }

    result = absence_module.absence_handler(USER_ID, task)

    mock_write.assert_called_once_with(
        USER_ID,
        {
            "date": "2026-11-12",
            "reason": "体調不良",
        },
    )

    assert "【欠勤連絡】" in result
    assert "2026-11-12" in result
    assert "店長へ通知します" in result


def test_absence_handler_handles_missing_date(monkeypatch):
    """日付が未指定でも保存関数にNoneを渡す"""

    mock_write = Mock()
    monkeypatch.setattr(absence_module, "write_absence", mock_write)

    result = absence_module.absence_handler(
        USER_ID,
        {"date": None},
    )

    mock_write.assert_called_once_with(
        USER_ID,
        {
            "date": None,
            "reason": "",
        },
    )

    assert "指定日の欠勤連絡" in result


def test_late_handler_writes_correct_data(monkeypatch):
    """遅刻連絡の内容を正しく保存関数に渡す"""

    mock_write = Mock()
    monkeypatch.setattr(late_module, "write_late", mock_write)

    task = {
        "mode": "arrival_time",
        "date": "2026-11-12",
        "arrival_time": "19:00",
        "delay_minutes": 60,
        "reason": "電車遅延",
    }

    result = late_module.late_handler(USER_ID, task)

    mock_write.assert_called_once_with(
        USER_ID,
        {
            "mode": "arrival_time",
            "date": "2026-11-12",
            "arrival_time": "19:00",
            "delay_minutes": 60,
            "reason": "電車遅延",
        },
    )

    assert "【遅刻連絡】" in result
    assert "2026-11-12" in result
    assert "19:00頃到着予定" in result


def test_late_handler_handles_missing_values(monkeypatch):
    """遅刻連絡の一部が未指定でもデフォルト値を設定する"""

    mock_write = Mock()
    monkeypatch.setattr(late_module, "write_late", mock_write)

    result = late_module.late_handler(
        USER_ID,
        {
            "date": None,
            "arrival_time": None,
        },
    )

    mock_write.assert_called_once_with(
        USER_ID,
        {
            "mode": None,
            "date": None,
            "arrival_time": None,
            "delay_minutes": None,
            "reason": "",
        },
    )

    assert "指定日の遅刻連絡" in result