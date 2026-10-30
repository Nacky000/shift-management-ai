# ShiftBot TODO

## 今やること

### 1. Spreadsheet構成・取得処理の確認
- [ ] 月別Spreadsheetの取得・作成処理を整理する
  - 通常運用では既存ファイルのみ取得する
  - 対象月のファイルが未作成の場合はエラーにする
- [ ] `create_monthly_template()` と `create_monthly_spreadsheet()` の役割を整理する
  - 現状の手動作成運用と、将来の自動作成機能を分離する
- [ ] 月別Spreadsheetの取得先を確認する
  - ファイル名による取得
  - 保存先フォルダ
  - 同名ファイルの重複対策
- [ ] 月別Spreadsheet内のシート構成を確認する
  - 5シートの存在確認
  - 不足しているシートがある場合の扱い
- [ ] シフト表の見出し構成を確認する
  - A1：空欄
  - A2：「スタッフ」
  - 1行目：日付
  - 2行目：曜日
- [ ] `spreadsheet.py` の重複定義を整理する
  - `ATTENDANCE_HEADERS` など
- [ ] 既存データを保持したままスタッフの追加・無効化に対応できるか確認する

### 2. LINEユーザー管理の実運用テスト
- [ ] LINEユーザー自動登録の動作確認
  - 初回登録
  - 重複登録防止
  - 状態別の返信
- [ ] 店長によるスタッフ状態変更の動作確認
  - 確認中 → 有効
  - 有効 → 無効
- [ ] 有効ユーザーのみがシフト登録できることを確認する

### 3. 各機能の実データテスト
- [ ] LINE webhook → `app.py` → `ai_parser` → `dispatcher` → `spreadsheet.py` の一連の動作確認
- [ ] 各機能の実データでの動作確認
  - schedule
  - absence
  - change
  - late
  - preference
  - memo
  - question
- [ ] 日付解決処理を含めた動作確認
  - 月日指定
  - 日付のみの指定
  - 相対日付
  - 曜日指定
  - 不正・曖昧な日付の確認処理

---

## 次にやること

### 1. Spreadsheet・データ管理の改善
- [ ] Google Sheets API設計改善（`user_id` 対応・DB化の検討）
- [ ] `spreadsheet.py` を実運用向けにリファクタリング（構造化・更新対応）
- [ ] シート構造の整理（日付・ユーザー・シフト管理）

### 2. 未実装機能の追加
- [ ] `question` のシート検索処理実装
- [ ] `memo` の保存先・読み出し処理の実装

### 3. 使いやすさ・運用面の改善
- [ ] LINE返信メッセージの整形
- [ ] 月別Spreadsheetの自動作成機能
  - 現状は手動作成で運用
  - 将来的に自動作成に対応
- [ ] 実運用を想定したエラー処理・ログの改善

### 4. 将来的な拡張機能
- [ ] 通知機能（Notification）
- [ ] 緊急連絡機能（Emergency）
- [ ] スタッフ募集機能（Recruitment）
- [ ] リマインド機能（Reminder）
- [ ] 曖昧な入力の判定機能（AmbiguousInput）

---

## 完了

### 1. 開発環境・基盤構築
- [x] GitHub構築
- [x] VSCode + WSL環境構築
- [x] `.gitignore` 設定
- [x] SSH認証
- [x] LINE公式アカウント作成
- [x] Messaging API設定
- [x] Webhook受信確認
- [x] `app.py` から返信できるようにする

### 2. AI解析・ルーティング
- [x] OpenAI APIキー取得
- [x] OpenAI API接続（基本動作確認）
- [x] システムプロンプト設計（ShiftBot）
- [x] JSONパース設計（`ai_parser.py`）
- [x] ルーティング設計（`dispatcher.py`）
- [x] handler設計（各type処理）
- [x] LINE → `app.py` → `ai_parser` → `dispatcher` の一連動作確認
- [x] handler → `spreadsheet.py` の連携確認（printベース）
- [x] 各typeごとの基本動作テスト（schedule / absence / change / late / preference / memo / question）

### 3. 日付解決処理
- [x] 日本時間（JST）での今日の日付取得
- [x] AIが解析した日付情報の実日付への変換
  - 月日指定（md）
  - 日付のみ指定（day）
  - 相対日付（relative）
  - 曜日指定（weekday）
- [x] 不正な日付・曖昧な日付の確認処理
- [x] 複数タスクの日付解決処理（`resolve_task_dates()`）
- [x] `dispatcher.py` への日付解決処理の組み込み
- [x] 日付エラーがあるタスクのSpreadsheetへの書き込み防止
- [x] 日付解決処理の基本テスト

### 4. Google Sheets連携
- [x] Google Sheets API設定（認証・サービスアカウント）
- [x] `spreadsheet.py` をGoogle Sheets API対応に変更
- [x] 月別Spreadsheetの手動作成・既存シートへのシフト登録確認
- [x] シフト登録時のセル色分け（新規・更新の識別）

### 5. スタッフ管理
- [x] `Users` シートのスタッフ管理構造を整備（`user_id` / `LINE表示名` / `名前` / `状態`）
- [x] スタッフ状態のプルダウン設定（確認中 / 有効 / 無効）
- [x] スタッフ状態の条件付き書式による色分け
- [x] `get_active_users()` による有効ユーザーの抽出
- [x] `get_user_status()` によるLINEユーザーの状態取得処理を追加
- [x] `app.py` にLINEユーザー自動登録・状態別の利用制限処理を組み込み

---

## 現在の運用上の注意

- OpenAI APIの利用にはクレジットが必要。API利用可能な状態になってから、実ユーザー入力での一連の動作テストを行う。
- 月別Spreadsheetは現状、手動作成を前提とする。
- 実運用テストが完了していない機能は、基本実装が済んでいても完了扱いにしない。