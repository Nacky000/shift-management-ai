# TODO

## 今やること
* [ ] LINE webhook → app.py → ai_parser → dispatcher → spreadsheet の実運用テスト（実ユーザー入力で確認）
* [ ] LINE user_id を取得してデータに含める設計準備


---

## 次にやること

* [ ] Google Sheets API設計改善（user_id対応・DB化）
* [ ] preadsheet.py を実運用向けにリファクタ（構造化・更新対応）
* [ ] シート構造設計（日付・ユーザー・シフト管理）
* [ ] question のシート検索処理実装
* [ ] LINE返信メッセージ整形

---

## 完了

* [x] GitHub構築
* [x] VSCode + WSL環境構築
* [x] .gitignore設定
* [x] SSH認証
* [x] LINE公式アカウント作成
* [x] Messaging API設定
* [x] Webhook受信確認
* [x] app.pyから返信できるようにする
* [x] OpenAI APIキー取得
* [x] OpenAI API接続（基本動作確認）
* [x] システムプロンプト設計（ShiftBot）
* [x] JSONパース設計（ai_parser.py）
* [x] ルーティング設計（dispatcher.py）
* [x] handler設計（各type処理）
* [x] spreadsheet.pyインターフェース作成
* [x] LINE → app.py → ai_parser → dispatcher の一連動作確認
* [x] handler → spreadsheet.py の連携確認（printベースでOK）
* [x] 各typeごとの最終動作テスト（schedule / absence / change / late / preference / memo / question）
* [x] Google Sheets API設定（認証・サービスアカウント）
* [x] spreadsheet.py をGoogle Sheets API対応に変更
