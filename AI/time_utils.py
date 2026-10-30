def to_minutes(time_text):
    """'18:30' などの時刻を0時からの経過分に変換する"""
    if not isinstance(time_text, str):
        raise TypeError("時刻は文字列で指定してください")

    parts = time_text.strip().split(":")
    if len(parts) != 2:
        raise ValueError("時刻は HH:MM 形式で指定してください")

    try:
        hour, minute = map(int, parts)
    except ValueError as e:
        raise ValueError("時刻は HH:MM 形式で指定してください") from e

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("時刻が範囲外です")

    return hour * 60 + minute