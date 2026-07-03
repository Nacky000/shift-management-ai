# schedule_handler.py

from Spreadsheet.spreadsheet import write_schedule

def schedule_handler(task):
    """
    シフト提出の処理
    """

    shifts = task.get("shifts", [])

    cleaned = []

    for s in shifts:
        cleaned.append({
            "date": s.get("date"),
            "start": s.get("start"),
            "end": s.get("end"),
            "memo": s.get("memo", "")
        })

    return write_schedule(cleaned)

# NOTE:
# - shiftsはAIの出力仕様に依存するため構造変更の可能性あり
# - start / end / memo は None の可能性を常に考慮する
# - dateも欠損するケースがある（曖昧入力）
# - spreadsheet層は保存専用で、ロジック判断は行わない
# - この関数は「AI出力 → DB用データ変換」の責務のみ持つ