from unittest.mock import Mock
from AI import dispatcher


USER_ID = "test_user_001"


def test_shift_task_calls_shift_handler(monkeypatch):
    """type=shift、action=writeならshift_handlerが呼ばれる"""
    mock_handler = Mock(return_value="シフト希望を登録しました")

    monkeypatch.setitem(dispatcher.HANDLERS, "shift", mock_handler)

    data = {
        "tasks": [
            {
                "action": "write",
                "type": "shift",
                "date": "2026-10-28",
                "start_time": "18:00",
                "end_time": "22:00",
                "ambiguity": [],
            }
        ]
    }

    result = dispatcher.dispatch_tasks(USER_ID, data)

    expected_task = {
        **data["tasks"][0],
        "date_error": None,
    }

    mock_handler.assert_called_once_with(USER_ID, expected_task)
    assert result == "シフト希望を登録しました"


def test_question_task_calls_question_handler(monkeypatch):
    """type=question，action=readならquestion_handlerが呼ばれる"""
    mock_handler = Mock(return_value="シフトについて回答します")

    monkeypatch.setitem(
        dispatcher.HANDLERS,
        "question",
        mock_handler,
    )

    task = {
        "action": "read",
        "type": "question",
        "content": "自分のシフトを教えて",
        "ambiguity": [],
    }

    result = dispatcher.dispatch_tasks(USER_ID, {"tasks": [task]})

    mock_handler.assert_called_once_with(USER_ID, task)
    assert result == "シフトについて回答します"


def test_invalid_action_does_not_call_handler(monkeypatch):
    """typeに対して不正なactionならhandlerを呼ばない"""
    mock_handler = Mock(return_value="登録成功")

    monkeypatch.setitem(dispatcher.HANDLERS, "shift", mock_handler)

    task = {
        "action": "read",  # shiftで許可されているのはwrite
        "type": "shift",
        "ambiguity": [],
    }

    result = dispatcher.dispatch_tasks(USER_ID, {"tasks": [task]})

    mock_handler.assert_not_called()
    assert result == dispatcher.ERROR_REPLY


def test_unknown_type_returns_error_reply():
    """未定義のtypeならエラー返信を返す"""
    task = {
        "action": None,
        "type": "unknown_type",
        "ambiguity": [],
    }

    result = dispatcher.dispatch_tasks(USER_ID, {"tasks": [task]})

    assert result == dispatcher.ERROR_REPLY


def test_handler_exception_returns_error_reply(monkeypatch):
    """handlerが例外を起こしてもエラー返信にする"""
    mock_handler = Mock(side_effect=RuntimeError("test error"))

    monkeypatch.setitem(dispatcher.HANDLERS, "shift", mock_handler)

    task = {
        "action": "write",
        "type": "shift",
        "ambiguity": [],
    }

    result = dispatcher.dispatch_tasks(USER_ID, {"tasks": [task]})

    mock_handler.assert_called_once_with(USER_ID, task)
    assert result == dispatcher.ERROR_REPLY


def test_shift_task_adds_default_date_error(monkeypatch):
    """date_errorがない場合、Noneが補完される"""

    mock_handler = Mock(return_value="登録成功")
    monkeypatch.setitem(dispatcher.HANDLERS, "shift", mock_handler)

    task = {
        "action": "write",
        "type": "shift",
        "date": "2026-11-12",
        "start_time": "18:00",
        "end_time": "22:00",
        "ambiguity": [],
    }

    dispatcher.dispatch_tasks(USER_ID, {"tasks": [task]})

    expected_task = {
        **task,
        "date_error": None,
    }

    mock_handler.assert_called_once_with(USER_ID, expected_task)


def test_shift_task_preserves_date_error(monkeypatch):
    """date_errorがある場合、handlerを呼ばず確認メッセージを返す"""

    mock_handler = Mock(return_value="確認が必要です")
    monkeypatch.setitem(dispatcher.HANDLERS, "shift", mock_handler)

    task = {
        "action": "write",
        "type": "shift",
        "date": None,
        "start_time": "18:00",
        "end_time": "22:00",
        "ambiguity": [],
        "date_error": "日付を特定できません",
    }

    result = dispatcher.dispatch_tasks(USER_ID, {"tasks": [task]})

    mock_handler.assert_not_called()

    assert "【日付の確認】" in result
    assert "日付を特定できません" in result
    assert "何月何日か確認して" in result