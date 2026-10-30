from datetime import date, datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

WEEKDAYS = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


def today_jst():
    """日本時間での今日の日付を返す。"""
    return datetime.now(JST).date()


def resolve_date(date_info, today=None):
    """
    AIが解析した日付情報を実際の日付に変換する。

    Args:
        date_info (dict): AIが解析した日付情報
        today (date, optional): テスト用の基準日

    Returns:
        dict:
            date_resolved: YYYY-MM-DD形式の日付。解決できない場合はNone
            needs_confirmation: 確認が必要かどうか
            reason: 確認が必要な理由
    """
    today = today or today_jst()


    def success(target_date):
        return {
            "date_resolved": target_date.isoformat(),
            "needs_confirmation": False,
            "reason": None,
        }

    def failure(reason):
        return {
            "date_resolved": None,
            "needs_confirmation": True,
            "reason": reason,
        }

    if not isinstance(date_info, dict):
        return failure("日付情報の形式が正しくありません。")

    kind = date_info.get("kind")

    try:
        # 例：「11月12日」
        if kind == "md":
            month = date_info.get("month")
            day = date_info.get("day")

            if not isinstance(month, int) or not isinstance(day, int):
                return failure("月または日が指定されていません。")

            year = date_info.get("year")

            if year is None:
                year = today.year

                target_date = date(year, month, day)

                # 今年の日付が過ぎていれば翌年にする
                if target_date < today:
                    target_date = date(year + 1, month, day)
            else:
                target_date = date(year, month, day)

            return success(target_date)

        # 例：「12日」
        elif kind == "day":
            day = date_info.get("day")

            if not isinstance(day, int):
                return failure("日が指定されていません。")

            # 翌月を計算
            if today.month == 12:
                year = today.year + 1
                month = 1
            else:
                year = today.year
                month = today.month + 1

            return success(date(year, month, day))

        # 例：「明日」「3日後」
        elif kind == "relative":
            days = date_info.get("days")

            if not isinstance(days, int):
                return failure("相対日付の日数が正しくありません。")

            return success(today + timedelta(days=days))

        # 例：「来週の木曜日」
        elif kind == "weekday":
            weekday = date_info.get("weekday")
            week = date_info.get("week")

            if weekday not in WEEKDAYS:
                return failure("曜日を正しく読み取れませんでした。")

            if week not in ("this", "next"):
                return failure("曜日の週を特定できません。")

            # 今週の月曜日
            this_monday = today - timedelta(days=today.weekday())

            # 今週または来週の月曜日
            base_monday = this_monday
            if week == "next":
                base_monday += timedelta(days=7)

            target_date = base_monday + timedelta(
                days=WEEKDAYS[weekday]
            )

            return success(target_date)

        else:
            return failure("日付の種類を判定できませんでした。")

    except (ValueError, TypeError, OverflowError):
        return failure("存在しない日付、または不正な日付です。")


