
import unittest
from datetime import date, datetime, timezone, timedelta

from AI.date_resolver import resolve_date


class TestDateResolver(unittest.TestCase):

    # 月が明示されている場合
    def test_explicit_month(self):
        result = resolve_date(
            {"kind": "md", "month": 11, "day": 12},
            today=date(2026, 10, 30)
        )

        self.assertEqual(result["date_resolved"], "2026-11-12")
        self.assertFalse(result["needs_confirmation"])

    # 指定された日付が過去なら翌年にする
    def test_explicit_month_past(self):
        result = resolve_date(
            {"kind": "md", "month": 2, "day": 10},
            today=date(2026, 10, 30)
        )

        self.assertEqual(result["date_resolved"], "2027-02-10")

    # 月が省略されている場合は翌月にする
    def test_day_only(self):
        result = resolve_date(
            {"kind": "day", "day": 12},
            today=date(2026, 10, 30)
        )

        self.assertEqual(result["date_resolved"], "2026-11-12")

    # 12月から翌年1月への年またぎ
    def test_day_only_year_transition(self):
        result = resolve_date(
            {"kind": "day", "day": 12},
            today=date(2026, 12, 20)
        )

        self.assertEqual(result["date_resolved"], "2027-01-12")

    # 相対日付
    def test_relative_date(self):
        result = resolve_date(
            {"kind": "relative", "days": 1},
            today=date(2026, 10, 30)
        )

        self.assertEqual(result["date_resolved"], "2026-10-31")

    # 今週の曜日
    def test_this_weekday(self):
        result = resolve_date(
            {
                "kind": "weekday",
                "weekday": "Thursday",
                "week": "this"
            },
            today=date(2026, 10, 30)
        )

        self.assertEqual(result["date_resolved"], "2026-10-29")

    # 来週の曜日
    def test_next_weekday(self):
        result = resolve_date(
            {
                "kind": "weekday",
                "weekday": "Thursday",
                "week": "next"
            },
            today=date(2026, 10, 30)
        )

        self.assertEqual(result["date_resolved"], "2026-11-05")

    # 存在しない日付
    def test_invalid_date(self):
        result = resolve_date(
            {"kind": "md", "month": 2, "day": 30},
            today=date(2026, 10, 30)
        )

        self.assertIsNone(result["date_resolved"])
        self.assertTrue(result["needs_confirmation"])
        self.assertIsNotNone(result["reason"])

    # 不正な日付形式
    def test_invalid_date_info(self):
        result = resolve_date(
            {"kind": "unknown"},
            today=date(2026, 10, 30)
        )

        self.assertIsNone(result["date_resolved"])
        self.assertTrue(result["needs_confirmation"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
