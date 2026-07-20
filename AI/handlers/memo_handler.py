# memo_handler.py

from Spreadsheet.spreadsheet import write_memo

def memo_handler(user_id,task):
    """
    メモの処理
    """

    cleaned = {
        "content": task.get("content", "")
    }

    # user_id と 整形済みデータ(cleaned) をスプレッドシートへ渡す
    write_memo(user_id, cleaned)

    # LINE側に返す確認メッセージ
    return "【メモ登録】\n伝言メモを登録しました．"