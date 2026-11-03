# AI/handlers/shift_handler.py

from datetime import date, timedelta

from AI.date_resolver import today_jst
from AI.time_utils import to_minutes
from Spreadsheet.spreadsheet import (
    write_schedule,
    write_change,
    get_shift,
)

WEEKDAY_JA = "月火水木金土日"
MAX_DAYS_AHEAD = 120


def _fmt_date(date_str):
    """'2026-10-24' -> '10/24(土)'"""
    d = date.fromisoformat(date_str)
    return f"{d.month}/{d.day}({WEEKDAY_JA[d.weekday()]})"


def _fmt_time(start_time, end_time):
    return f"{start_time or '未定'}〜{end_time or '未定'}"


def check_shift(task, today=None):
    """
    登録前の確認項目と警告を返す。
    questions が空なら次の処理へ進んでよい。
    warnings は処理を止めない。
    """
    questions = []
    warnings = []

    today = today or today_jst()
    resolved = task.get("date")
    ambiguity = task.get("ambiguity") or []
    action = task.get("action")

    # 1. 日付の確認
    if resolved is None:
        if task.get("date_error"):
            questions.append(
                f"日付を解決できませんでした．"
                f"{task['date_error']} 日付を確認してください．"
            )
        else:
            questions.append("日付を教えてください．")
    else:
        try:
            d = date.fromisoformat(resolved)
        except (TypeError, ValueError):
            questions.append(
                "日付を正しく読み取れませんでした．日付を確認してください．"
            )
        else:
            if d < today:
                warnings.append(
                    f"{_fmt_date(resolved)} は過去の日付です．"
                )
            elif d > today + timedelta(days=MAX_DAYS_AHEAD):
                warnings.append(
                    f"{_fmt_date(resolved)} は120日より先の日付です．"
                )

    # 2. 時刻の確認
    if action == "change":
        start_time = task.get("new_start_time")
        end_time = task.get("new_end_time")
    else:
        start_time = task.get("start_time")
        end_time = task.get("end_time")

    if "ampm_unclear" in ambiguity and (start_time or end_time):
        questions.append("時刻は午前ですか，午後ですか？")

    no_time = not start_time and not end_time

    if "time_unclear" in ambiguity or (
        action == "write" and no_time
    ):
        questions.append(
            "開始・終了時刻を教えてください．"
            "(例: 18時〜22時)"
        )

    if start_time and end_time:
        try:
            if to_minutes(start_time) == to_minutes(end_time):
                questions.append(
                    "開始と終了が同じ時刻です．確認してください．"
                )
        except (TypeError, ValueError):
            questions.append("時刻の形式を確認してください．")

    # 3. 分類の確認
    if "type_unclear" in ambiguity:
        questions.append(
            "提出内容を読み取れませんでした．"
            "「20日は18時から22時で入れます」のように送ってください．"
        )

    return questions, warnings


def shift_handler(user_id, task):
    """
    シフト希望の登録・更新と変更申請を処理する。

    action == "write":
        write_schedule() でシフト希望を登録・更新する。

    action == "change":
        既存シフトを確認し、write_change() で変更申請を記録する。
    """

    # 1. 登録前の確認
    questions, warnings = check_shift(task)

    if questions:
        return "【確認】\n" + "\n".join(questions)

    date_str = task["date"]
    new_start_time = task.get("start_time")
    new_end_time = task.get("end_time")
    old_start_time = task.get("old_start_time")
    old_end_time = task.get("old_end_time")
    memo = task.get("memo") or ""
    action = task.get("action")

    # 2. 新規提出・シフト希望の更新
    if action == "write":
        # write_schedule() は1件分の辞書を受け取る。
        # start_time / end_time が None の場合も
        # write_schedule() 側で「未定」として保存する。
        write_schedule(
            user_id,
            {
                "date": date_str,
                "start_time": new_start_time,
                "end_time": new_end_time,
                "memo": memo,
            },
        )

        return _append_warnings(
            (
                f"【シフト希望】\n"
                f"{_fmt_date(date_str)} "
                f"{_fmt_time(new_start_time, new_end_time)} "
                f"の登録を受け付けました．"
            ),
            warnings,
        )

    # 3. 変更申請の場合
    elif action == "change":

        existing = get_shift(user_id, date_str)

        if existing is None:
            return (
                f"【確認】\n"
                f"{_fmt_date(date_str)}の登録済みシフトが見つかりません．\n"
                f"新規で登録する場合は「日付＋時間」で送ってください．\n"
                f"(例: 20日は18時から22時で入れます)"
            )

        # 4. 変更前の時刻が指定されていれば既存シフトと照合
        mismatch = (
            (old_start_time and old_start_time != existing.get("start"))
            or (old_end_time and old_end_time != existing.get("end"))
        )

        if mismatch:
            return (
                f"【確認】\n"
                f"{_fmt_date(date_str)}の登録済みシフトは "
                f"{_fmt_time(existing.get('start'), existing.get('end'))} です．\n"
                f"変更前の時間が違うようです．"
                f"内容を確認してもう一度送ってください．"
            )

        # 5. 変更しない時刻は既存シフトの値を維持
        if "new_start_time" in task:
            new_start_time = task["new_start_time"]
        else:
            new_start_time = existing.get("start")

        if "new_end_time" in task:
            new_end_time = task["new_end_time"]
        else:
            new_end_time = existing.get("end")

        # 6. 変更後の時刻が両方未入力なら確認
        if not new_start_time and not new_end_time:
            return (
                "【確認】\n"
                "変更後の開始・終了時刻を確認できませんでした．\n"
                "変更後の時間を教えてください．"
            )

        # 7. 変更申請を記録
        write_change(user_id, {
            "date": date_str,
            "old_start_time": existing.get("start"),
            "old_end_time": existing.get("end"),
            "new_start_time": new_start_time,
            "new_end_time": new_end_time,
            "memo": task.get("memo") or "",
            "reason": task.get("reason") or ""
        })

        return _append_warnings(
            (
                f"【シフト変更申請】\n"
                f"{_fmt_date(date_str)} "
                f"{_fmt_time(existing.get('start'), existing.get('end'))} → "
                f"{_fmt_time(new_start_time, new_end_time)} "
                f"の変更申請を受け付けました．"
            ),
            warnings,
        )

    else:
        return "【エラー】シフト処理のactionが正しくありません．"


def _append_warnings(message, warnings):
    if warnings:
        message += "\n\n【警告】\n" + "\n".join(warnings)
    return message