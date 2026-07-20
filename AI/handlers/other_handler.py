# other_handler.py

def other_handler(user_id, task):  # user_id を追加
    """
    分類不能、またはその他処理
    """
    print(f"OTHER [User: {user_id}]:", task)
    
    # LINE側に返す確認メッセージ
    return "申し訳ありません．メッセージの内容をうまく理解できませんでした．シフトの提出や変更，遅刻・欠勤の連絡などをもう一度分かりやすく送信してください．"