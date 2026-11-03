from unittest.mock import Mock

from AI.handlers import shift_handler as handler


USER_ID = "test_user_001"


def setup_change_test(monkeypatch, existing=None):
    """日付と既存シフトを固定して変更申請をテストする"""

    monkeypatch.setattr(
        handler,
        "today_jst",
        Mock(return_value=__import__("datetime").date(2026, 11, 3)),
    )

    monkeypatch.setattr(
        handler,
        "get_shift",
        Mock(return_value=existing),
    )

    mock_write_change = Mock()
    monkeypatch.setattr(handler, "write_change", mock_write_change)

    return mock_write_change


def test_change_handler_writes_change_request(monkeypatch):
    """既存シフトを確認して変更申請を記録する"""

    mock_write_change = setup_change_test(
        monkeypatch,
        existing={"start": "18:00", "end": "22:00"},
    )

    task = {
        "action": "change",
        "date": "2026-11-12",
        "old_start_time": "18:00",
        "old_end_time": "22:00",
        "new_start_time": "19:00",
        "new_end_time": "23:00",
        "memo": "授業のため",
        "reason": "予定変更",
        "ambiguity": [],
    }

    result = handler.shift_handler(USER_ID, task)

    mock_write_change.assert_called_once_with(
        USER_ID,
        {
            "date": "2026-11-12",
            "old_start_time": "18:00",
            "old_end_time": "22:00",
            "new_start_time": "19:00",
            "new_end_time": "23:00",
            "memo": "授業のため",
            "reason": "予定変更",
        },
    )

    assert "【シフト変更申請】" in result
    assert "18:00〜22:00 → 19:00〜23:00" in result


def test_change_handler_rejects_missing_existing_shift(monkeypatch):
    """登録済みシフトがなければ変更申請を記録しない"""

    mock_write_change = setup_change_test(monkeypatch, existing=None)

    task = {
        "action": "change",
        "date": "2026-11-12",
        "new_start_time": "19:00",
        "new_end_time": "23:00",
        "ambiguity": [],
    }

    result = handler.shift_handler(USER_ID, task)

    mock_write_change.assert_not_called()
    assert "登録済みシフトが見つかりません" in result


def test_change_handler_rejects_old_time_mismatch(monkeypatch):
    """変更前の時刻が登録済みシフトと違えば申請しない"""

    mock_write_change = setup_change_test(
        monkeypatch,
        existing={"start": "18:00", "end": "22:00"},
    )

    task = {
        "action": "change",
        "date": "2026-11-12",
        "old_start_time": "17:00",
        "old_end_time": "22:00",
        "new_start_time": "19:00",
        "new_end_time": "23:00",
        "ambiguity": [],
    }

    result = handler.shift_handler(USER_ID, task)

    mock_write_change.assert_not_called()
    assert "変更前の時間が違うようです" in result


def test_change_handler_preserves_unchanged_time(monkeypatch):
    """変更後の時刻が片方だけ指定された場合、もう片方は既存値を使う"""

    mock_write_change = setup_change_test(
        monkeypatch,
        existing={"start": "18:00", "end": "22:00"},
    )

    task = {
        "action": "change",
        "date": "2026-11-12",
        "new_start_time": "19:00",
        "ambiguity": [],
    }

    handler.shift_handler(USER_ID, task)

    mock_write_change.assert_called_once_with(
        USER_ID,
        {
            "date": "2026-11-12",
            "old_start_time": "18:00",
            "old_end_time": "22:00",
            "new_start_time": "19:00",
            "new_end_time": "22:00",
            "memo": "",
            "reason": "",
        },
    )


def test_change_handler_rejects_both_new_times_missing(monkeypatch):
    """変更後の時刻が両方Noneなら申請しない"""

    mock_write_change = setup_change_test(
        monkeypatch,
        existing={"start": "18:00", "end": "22:00"},
    )

    task = {
        "action": "change",
        "date": "2026-11-12",
        "new_start_time": None,
        "new_end_time": None,
        "ambiguity": [],
    }

    result = handler.shift_handler(USER_ID, task)

    mock_write_change.assert_not_called()
    assert "変更後の開始・終了時刻を確認できませんでした" in result