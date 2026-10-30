from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from LINE import app as line_app


@pytest.fixture
def mocks(monkeypatch):
    """外部API・Spreadsheet・AI処理をモックに置き換える"""

    mock_spreadsheet = Mock()
    mock_line_api = Mock()
    mock_ai_parser = Mock()
    mock_dispatcher = Mock()

    monkeypatch.setattr(
        line_app.spreadsheet,
        "get_user_status",
        mock_spreadsheet.get_user_status
    )
    monkeypatch.setattr(
        line_app.spreadsheet,
        "register_user",
        mock_spreadsheet.register_user
    )
    monkeypatch.setattr(
        line_app.line_bot_api,
        "get_profile",
        mock_line_api.get_profile
    )
    monkeypatch.setattr(
        line_app.line_bot_api,
        "reply_message",
        mock_line_api.reply_message
    )
    monkeypatch.setattr(
        line_app.ai_parser,
        "parse_message",
        mock_ai_parser.parse_message
    )
    monkeypatch.setattr(
        line_app.dispatcher,
        "dispatch_tasks",
        mock_dispatcher.dispatch_tasks
    )

    mock_line_api.get_profile.return_value = SimpleNamespace(
        display_name="テストユーザー"
    )

    mock_ai_parser.parse_message.return_value = {
        "action": "question"
    }
    mock_dispatcher.dispatch_tasks.return_value = "AI処理結果"

    return {
        "spreadsheet": mock_spreadsheet,
        "line_api": mock_line_api,
        "ai_parser": mock_ai_parser,
        "dispatcher": mock_dispatcher,
    }


def make_event():
    """LINEから届くイベントを再現する"""
    return SimpleNamespace(
        source=SimpleNamespace(user_id="U001"),
        message=SimpleNamespace(text="明日のシフトを確認したい"),
        reply_token="test_reply_token"
    )


def get_reply_text(mocks):
    """LINEへの返信メッセージ本文を取得する"""
    call_args = mocks["line_api"].reply_message.call_args

    assert call_args is not None

    message = call_args.args[1]
    return message.text


# -----------------------------
# 1. 未登録ユーザー
# -----------------------------

def test_unregistered_user(mocks):
    mocks["spreadsheet"].get_user_status.return_value = None
    mocks["spreadsheet"].register_user.return_value = True

    line_app.handle_message(make_event())

    mocks["line_api"].get_profile.assert_called_once_with("U001")
    mocks["spreadsheet"].register_user.assert_called_once_with(
        "U001",
        "テストユーザー"
    )

    assert "初回登録を受け付けました" in get_reply_text(mocks)

    mocks["ai_parser"].parse_message.assert_not_called()
    mocks["dispatcher"].dispatch_tasks.assert_not_called()


# -----------------------------
# 2. 確認中ユーザー
# -----------------------------

def test_pending_user(mocks):
    mocks["spreadsheet"].get_user_status.return_value = "確認中"

    line_app.handle_message(make_event())

    assert "店長の確認待ち" in get_reply_text(mocks)

    mocks["ai_parser"].parse_message.assert_not_called()
    mocks["dispatcher"].dispatch_tasks.assert_not_called()


# -----------------------------
# 3. 有効ユーザー
# -----------------------------

def test_active_user(mocks):
    mocks["spreadsheet"].get_user_status.return_value = "有効"

    line_app.handle_message(make_event())

    mocks["ai_parser"].parse_message.assert_called_once_with(
        "明日のシフトを確認したい"
    )

    mocks["dispatcher"].dispatch_tasks.assert_called_once_with(
        "U001",
        {"action": "question"}
    )

    assert get_reply_text(mocks) == "AI処理結果"


# -----------------------------
# 4. 無効ユーザー
# -----------------------------

def test_disabled_user(mocks):
    mocks["spreadsheet"].get_user_status.return_value = "無効"

    line_app.handle_message(make_event())

    assert "利用できません" in get_reply_text(mocks)

    mocks["ai_parser"].parse_message.assert_not_called()
    mocks["dispatcher"].dispatch_tasks.assert_not_called()


# -----------------------------
# 5. 不明な状態
# -----------------------------

def test_unknown_status(mocks):
    mocks["spreadsheet"].get_user_status.return_value = "不明"

    line_app.handle_message(make_event())

    assert "状態を確認できません" in get_reply_text(mocks)

    mocks["ai_parser"].parse_message.assert_not_called()
    mocks["dispatcher"].dispatch_tasks.assert_not_called()


# -----------------------------
# 6. 登録処理が重複で失敗した場合
# -----------------------------

def test_registration_duplicate_active_user(mocks):
    mocks["spreadsheet"].get_user_status.side_effect = [
        None,
        "有効"
    ]
    mocks["spreadsheet"].register_user.return_value = False

    line_app.handle_message(make_event())

    assert mocks["spreadsheet"].get_user_status.call_count == 2

    mocks["ai_parser"].parse_message.assert_called_once()
    mocks["dispatcher"].dispatch_tasks.assert_called_once()

    assert get_reply_text(mocks) == "AI処理結果"