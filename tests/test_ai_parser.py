# OpenAI APIを実際には呼び出さずにシフト提出の解析結果を正しく読み取れるかテスト
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from AI.ai_parser import parse_message


class TestAIParser(unittest.TestCase):

    def test_parse_six_shift_tasks(self):
        expected_tasks = [
            {
                "action": "write",
                "type": "shift",
                "date": f"2026-11-{day:02d}",
                "start": start,
                "end": end,
                "ambiguity": [],
            }
            for day, start, end in [
                (2, "11:00", "16:00"),
                (5, "11:00", "15:00"),
                (12, "11:00", "15:00"),
                (18, "11:00", "15:00"),
                (26, "11:00", "15:00"),
                (27, "11:00", "13:00"),
            ]
        ]

        fake_response = SimpleNamespace(
            output_text=json.dumps(
                {"tasks": expected_tasks},
                ensure_ascii=False,
            )
        )

        with patch(
            "AI.ai_parser.client.responses.create",
            return_value=fake_response,
        ) as mock_create:
            result = parse_message(
                "11月のシフト希望（テスト用メッセージ）"
            )

        mock_create.assert_called_once()
        self.assertEqual(len(result["tasks"]), 6)
        self.assertEqual(result["tasks"], expected_tasks)


if __name__ == "__main__":
    unittest.main(verbosity=2)
