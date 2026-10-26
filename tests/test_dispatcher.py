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

    mock_handler.assert_called_once_with(USER_ID, data["tasks"][0])
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
