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


def _fmt_time(start, end):
    return f"{start or '未定'}〜{end or '未定'}"


def check_shift(task, today=None):
    """
    登録前の確認項目を返す。
    空リストなら次の処理へ進んでよい。

    Parameters
    ----------
    task : dict
        normalize_tasks 通過後のタスク。
        date_resolved: YYYY-MM-DD または None
        date_written: 元の日付表現
    today : datetime.date, optional
        テスト時に使用する基準日。
        指定しなければ today_jst() を使用する。
    """
    questions = []

    today = today or today_jst()

    resolved = task.get("date_resolved")
    ambiguity = task.get("ambiguity") or []
    change_hint = task.get("change_hint") is True

    # 1. 日付の確認
    if resolved is None:
        if task.get("date_written"):
            questions.append(
                "その日付は存在しないようです．日付を確認してください．"
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
                questions.append(
                    f"{_fmt_date(resolved)} は過去の日付です．"
                    "間違いありませんか？"
                )
            elif d > today + timedelta(days=MAX_DAYS_AHEAD):
                questions.append(
                    f"{_fmt_date(resolved)} はかなり先の日付です．"
                    "間違いありませんか？"
                )

    # 2. 時刻の確認
    start = task.get("start")
    end = task.get("end")

    if "ampm_unclear" in ambiguity and (start or end):
        questions.append("時刻は午前ですか，午後ですか？")

    no_time = not start and not end

    # 時刻が不明、または新規提出で両方未入力の場合
    if "time_unclear" in ambiguity or (
        not change_hint and no_time
    ):
        questions.append(
            "開始・終了時刻を教えてください．"
            "(例: 18時〜22時)"
        )

    # 開始・終了の両方が指定されている場合は整合性を確認
    if start and end:
        try:
            if to_minutes(start) == to_minutes(end):
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

    return questions


def shift_handler(user_id, task):
    """
    シフト希望の登録・更新と変更申請を処理する。

    change_hint = false:
        write_schedule() でシフト希望を登録・更新する。

    change_hint = true:
        既存シフトを確認し、write_change() で変更申請を記録する。
    """

    # 1. 登録前の確認
    questions = check_shift(task)

    if questions:
        return "【確認】\n" + "\n".join(questions)

    date_str = task["date_resolved"]
    new_start = task.get("start")
    new_end = task.get("end")
    old_start = task.get("old_start")
    old_end = task.get("old_end")
    memo = task.get("memo") or ""
    change_hint = task.get("change_hint") is True

    # 2. 新規提出・シフト希望の更新
    if not change_hint:
        # write_schedule() は1件分の辞書を受け取る。
        # start/end が None の場合の保存方法は、
        # spreadsheet.py 側でも対応させる必要がある。
        write_schedule(
            user_id,
            {
                "date": date_str,
                "start": new_start,
                "end": new_end,
                "memo": memo,
            },
        )

        return (
            f"【シフト希望】\n"
            f"{_fmt_date(date_str)} "
            f"{_fmt_time(new_start, new_end)} "
            f"の登録を受け付けました．"
        )

    # 3. 変更申請の場合は既存シフトを取得
    existing = get_shift(user_id, date_str)

    if existing is None:
        return (
            f"【確認】\n"
            f"{_fmt_date(date_str)}の登録済みシフトが見つかりません．\n"
            f"新規で登録する場合は「日付＋時間」で送ってください．\n"
            f"(例: 20日は18時から22時で入れます)"
        )

    # 4. 変更前の時刻が指定されていれば既存シフトと照合
    # get_shift() が返す時刻は HH:MM 形式に正規化されていることを想定。
    mismatch = (
        (old_start and old_start != existing.get("start"))
        or (old_end and old_end != existing.get("end"))
    )

    if mismatch:
        return (
            f"【確認】\n"
            f"{_fmt_date(date_str)}の登録済みシフトは "
            f"{_fmt_time(existing.get('start'), existing.get('end'))} です．\n"
            f"変更前の時間が違うようです．"
            f"内容を確認してもう一度送ってください．"
        )

    # 5. 変更後の時刻が両方未入力なら確認
    if not new_start and not new_end:
        return (
            "【確認】\n"
            "変更後の時間を教えてください．\n"
            "(例: 20日を19時から22時に変更)"
        )

    # 6. 変更しない時刻は既存シフトの値を維持
    new_start = new_start or existing.get("start")
    new_end = new_end or existing.get("end")

    if not new_start or not new_end:
        return (
            "【確認】\n"
            "変更後の開始・終了時刻を確認できませんでした．\n"
            "変更後の時間を教えてください．"
        )

    # 7. 変更申請を記録
    write_change(
        user_id,
        {
            "date": date_str,
            "old_start": existing.get("start"),
            "old_end": existing.get("end"),
            "new_start": new_start,
            "new_end": new_end,
        },
    )

    return (
        f"【シフト変更申請】\n"
        f"{_fmt_date(date_str)} "
        f"{_fmt_time(existing.get('start'), existing.get('end'))} → "
        f"{_fmt_time(new_start, new_end)} "
        f"の変更申請を受け付けました．"
    )