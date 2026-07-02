# ShiftBot

LINE × OpenAI を活用したシフト管理自動化システム

---

## 📌 概要

ShiftBotは，飲食店におけるシフト提出・変更・欠勤連絡などを
LINEの自然な文章入力から自動で構造化し，Googleスプレッドシートへ反映するシステムである．

従来の「フォーマット入力」や「手動転記」を不要にし，
スタッフの負担と管理コストを削減することを目的とする．

---

## 🚀 主な機能

- LINEによるシフト提出・変更・欠勤・遅刻連絡
- OpenAIによる自然言語解析 → JSON化
- 複数タスクの同時処理対応
- シフトデータの構造化管理
- Googleスプレッドシートへの自動反映（実装予定）
- リマインダー通知（実装予定）

---

## 🧠 システム構成

```text
LINE
 ↓
Webhook (app.py)
 ↓
OpenAI API (ai_parser.py)
 ↓
Dispatcher (task routing)
 ↓
Handlers (業務別処理)
 ↓
Spreadsheet API
 ↓
Google Sheets
```

## 🛠 技術スタック
- Python
- OpenAI API (GPT-5 mini)
- LINE Messaging API
- Google Sheets API
- VSCode
- GitHub

## ⚙️ 設計思想
- 自然言語入力を前提としたUIレス設計
- 機能ごとのhandler分離による拡張性確保
- JSONベースの中間データ構造による疎結合設計
- 外部API依存部分（Sheets等）を分離し保守性を向上