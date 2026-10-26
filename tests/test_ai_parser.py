import json
from unittest.mock import Mock

from AI import ai_parser


def mock_openai_response(monkeypatch, output_text):
    """OpenAI Responses APIの応答を模擬する"""
    response = Mock()
    response.output_text = output_text

    monkeypatch.setattr(
        ai_parser.client.responses,
        "create",
        Mock(return_value=response),
    )


def test_parse_schedule_message(monkeypatch):
    """シフト入力が期待するtasks形式になるか"""
    expected = {
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

    mock_openai_response(
        monkeypatch,
        json.dumps(expected, ensure_ascii=False),
    )

    result = ai_parser.parse_message("10月28日 18時から22時まで")

    assert result == expected
    assert isinstance(result, dict)
    assert isinstance(result["tasks"], list)
    assert result["tasks"][0]["type"] == "shift"
    assert result["tasks"][0]["action"] == "write"


def test_parse_invalid_json_returns_other_task(monkeypatch):
    """AIが不正なJSONを返したらotherにフォールバックする"""
    mock_openai_response(monkeypatch, "これはJSONではありません")

    result = ai_parser.parse_message("テストメッセージ")

    assert result == {
        "tasks": [
            {
                "action": None,
                "type": "other",
                "content": "テストメッセージ",
                "ambiguity": [],
            }
        ]
    }


def test_parse_api_error_returns_other_task(monkeypatch):
    """OpenAI APIで例外が起きた場合もotherにフォールバックする"""
    monkeypatch.setattr(
        ai_parser.client.responses,
        "create",
        Mock(side_effect=Exception("API error")),
    )

    result = ai_parser.parse_message("テストメッセージ")

    assert result["tasks"][0]["type"] == "other"
    assert result["tasks"][0]["content"] == "テストメッセージ"
