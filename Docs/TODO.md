# ShiftBot TODO

## 今やること

- [ ] LINE webhook → `app.py` → `ai_parser` → `dispatcher` → `spreadsheet` の実運用テスト（実ユーザー入力で確認）
- [ ] LINEユーザー自動登録の動作テスト（初回登録・重複登録防止・状態別の返信）
- [ ] 店長によるスタッフ状態変更（確認中 → 有効）の動作確認
- [ ] 有効ユーザーのみがシフト登録できることを確認
- [ ] 各機能の実データでの動作確認（schedule / absence / change / late / preference / memo / question）
- [ ] 月別Spreadsheetの取得・作成処理を整理（通常運用では既存ファイルのみ取得し、未作成の場合はエラーにする）
- [ ] `create_monthly_template()` と `create_monthly_spreadsheet()` の役割を整理（手動作成での運用と、将来の自動作成機能を分離）
- [ ] 月別Spreadsheetの取得先を確認（名前による取得・保存先フォルダ・同名ファイルの重複対策）
- [ ] 月別Spreadsheet内のシート構成を確認（5シートの存在確認・不足時の扱い）
- [ ] シフト表の見出し構成を確認（A1空欄、A2「スタッフ」、1行目の日付、2行目の曜日）
- [ ] `spreadsheet.py` の重複定義を整理（`ATTENDANCE_HEADERS` など）
- [ ] 既存データを保持したままスタッフの追加・無効化に対応できるか確認

---

## 次にやること

- [ ] Google Sheets API設計改善（`user_id` 対応・DB化の検討）
- [ ] `spreadsheet.py` を実運用向けにリファクタ（構造化・更新対応）
- [ ] シート構造の整理（日付・ユーザー・シフト管理）
- [ ] `question` のシート検索処理実装
- [ ] `memo` の保存先・読み出し処理の実装
- [ ] LINE返信メッセージ整形
- [ ] 月別スプレッドシートの自動作成機能（現状は手動作成で運用、将来対応）
- [ ] 実運用を想定したエラー処理・ログの改善

---

## 完了

- [x] GitHub構築
- [x] VSCode + WSL環境構築
- [x] `.gitignore` 設定
- [x] SSH認証
- [x] LINE公式アカウント作成
- [x] Messaging API設定
- [x] Webhook受信確認
- [x] `app.py` から返信できるようにする
- [x] OpenAI APIキー取得
- [x] OpenAI API接続（基本動作確認）
- [x] システムプロンプト設計（ShiftBot）
- [x] JSONパース設計（`ai_parser.py`）
- [x] ルーティング設計（`dispatcher.py`）
- [x] handler設計（各type処理）
- [x] `spreadsheet.py` インターフェース作成
- [x] LINE → `app.py` → `ai_parser` → `dispatcher` の一連動作確認
- [x] handler → `spreadsheet.py` の連携確認（printベース）
- [x] 各typeごとの基本動作テスト（schedule / absence / change / late / preference / memo / question）
- [x] Google Sheets API設定（認証・サービスアカウント）
- [x] `spreadsheet.py` をGoogle Sheets API対応に変更
- [x] 月別スプレッドシートの手動作成・既存シートへのシフト登録確認
- [x] シフト登録時のセル色分け（新規・更新の識別）
- [x] `Users` シートのスタッフ管理構造を整備（`user_id` / `LINE表示名` / `名前` / `状態`）
- [x] スタッフ状態のプルダウン設定（確認中 / 有効 / 無効）
- [x] スタッフ状態の条件付き書式による色分け
- [x] `get_active_users()` による有効ユーザーの抽出
- [x] `get_user_status()` によるLINEユーザーの状態取得処理を追加
- [x] `app.py` にLINEユーザー自動登録・状態別の利用制限処理を組み込み（実運用テストは未完了）
