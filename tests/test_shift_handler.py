# シートの書き込みは行わず，コードでのシフト提出に対して日付・時刻の確認が通るかを試す
import unittest
from datetime import date
from unittest.mock import patch

from AI.handlers.shift_handler import check_shift
from AI import dispatcher


class TestShiftHandler(unittest.TestCase):
    """シフト確認処理のテストであり，シートへの書き込みは行わない．"""

    def test_six_shift_requests(self):
        """11月の6日分について、日付・時刻の確認が通るか。"""
        test_cases = [
            ("2026-11-02", "11:00", "16:00"),
            ("2026-11-05", "11:00", "15:00"),
            ("2026-11-12", "11:00", "15:00"),
            ("2026-11-18", "11:00", "15:00"),
            ("2026-11-26", "11:00", "15:00"),
            ("2026-11-27", "11:00", "13:00"),
        ]

        for date_str, start, end in test_cases:
            with self.subTest(date=date_str):
                task = {
                    "date_resolved": date_str,
                    "date_written": date_str,
                    "start": start,
                    "end": end,
                    "ambiguity": [],
                    "change_hint": False,
                }

                questions = check_shift(
                    task,
                    today=date(2026, 10, 27),
                )

                self.assertEqual(
                    questions,
                    [],
                    f"{date_str}: {questions}",
                )

    def test_dispatch_six_tasks_without_writing(self):
        """dispatcherの振り分けだけをテストする。"""
        tasks = [
            {
                "action": "write",
                "type": "shift",
                "date_resolved": date_str,
                "start": start,
                "end": end,
                "ambiguity": [],
            }
            for date_str, start, end in [
                ("2026-11-02", "11:00", "16:00"),
                ("2026-11-05", "11:00", "15:00"),
                ("2026-11-12", "11:00", "15:00"),
                ("2026-11-18", "11:00", "15:00"),
                ("2026-11-26", "11:00", "15:00"),
                ("2026-11-27", "11:00", "13:00"),
            ]
        ]

        received = []

        def fake_shift_handler(user_id, task):
            received.append(task)
            return "テスト成功"

        with patch.dict(
            dispatcher.HANDLERS,
            {"shift": fake_shift_handler},
        ):
            result = dispatcher.dispatch_tasks(
                "TEST_USER",
                {"tasks": tasks},
            )

        self.assertEqual(len(received), 6)
        self.assertEqual(result.splitlines(), ["テスト成功"] * 6)
        self.assertEqual(
            [task["date_resolved"] for task in received],
            [
                "2026-11-02",
                "2026-11-05",
                "2026-11-12",
                "2026-11-18",
                "2026-11-26",
                "2026-11-27",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
