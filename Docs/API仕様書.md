# API仕様書

## 1. parse_message()

役割：LINEから受け取った自由記述をAIで解析し、タスク形式の構造化データに変換する。

入力例

```text
6/10 18-22でシフトに入りたい
```

出力例

```json
{
  "tasks": [
    {
      "type": "shift",
      "action": "write",
      "date": {
        "kind": "md",
        "month": 6,
        "day": 10
      },
      "start_time": "18:00",
      "end_time": "22:00",
      "memo": ""
    }
  ]
}
```

※実際の日付への変換は `date_resolver.py` が担当する。

---

## 2. resolve_task_dates()

役割：AIが解析した日付情報を実際の日付（YYYY-MM-DD）に変換する。

入力例

```json
{
  "tasks": [
    {
      "type": "shift",
      "date": {
        "kind": "md",
        "month": 6,
        "day": 10
      }
    }
  ]
}
```

出力例

```json
{
  "tasks": [
    {
      "type": "shift",
      "date": "2027-06-10",
      "date_error": null
    }
  ]
}
```

※年を省略した場合、過去の日付なら翌年として解決する。日付を特定できない場合は確認を求め、Spreadsheetへの書き込みを行わない。

---

## 3. dispatch_tasks()

役割：解析・日付解決済みのタスクを適切なhandlerへ振り分け、返信内容をまとめる。

入力例

```json
{
  "tasks": [
    {
      "type": "shift",
      "action": "write",
      "date": "2027-06-10",
      "start_time": "18:00",
      "end_time": "22:00"
    }
  ]
}
```

出力例

```text
6月10日18:00～22:00で登録しました。
```

---

## 4. write_schedule()

役割：シフト希望を対象月のGoogle Spreadsheetへ書き込む。

入力例

```json
{
  "date": "2027-06-10",
  "start_time": "18:00",
  "end_time": "22:00"
}
```

※スタッフ情報は `user_id` から取得する設計を想定する。実際の引数・保存形式は `spreadsheet.py` の実装に合わせる。

---

## 5. write_change()

役割：既存のシフト希望を変更する。

入力例

```json
{
  "date": "2027-06-10",
  "start_time": "20:00",
  "end_time": "22:00"
}
```

※実際の引数・更新方法は `spreadsheet.py` の実装に合わせる。

---

## 6. send_reply()

役割：処理結果や確認事項をLINEへ返信する。

返信例

```text
6月10日18:00～22:00で登録しました。
修正がある場合はそのまま送信してください。
```

※返信処理は `LINE/app.py` が担当する。

---

## 7. remind()

役割：シフト未提出者へ催促メッセージを送信する。

送信例

```text
シフト未提出の方にお送りしています。
シフトの提出期限は本日です。
期限内に送信をお願いします。
```

※現時点では将来的な拡張機能。未提出者の判定やLINEへの一斉送信処理は今後実装する。