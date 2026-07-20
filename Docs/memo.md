# ShiftBot 開発メモ

---

# ■ 実行手順

## 動作確認

<!-- cd /mnt/c/Myprojects/shift-management-ai
source .venv/Scripts/activate
PYTHONPATH=. python3 LINE/app.py -->

ターミナル1
```bash
python3 LINE/app.py
```
ターミナル2
```bash
cd /mnt/c/Myprojects/shift-management-ai/Tools
./ngrok http 10.160.65.252:5000
```

## Git操作
```bash
git add .
git commit -m "update"
git push origin main
```

## コミット方法
feat: → 機能追加（今回これ）
fix: → バグ修正
refactor: → 設計変更
chore: → 環境・設定系