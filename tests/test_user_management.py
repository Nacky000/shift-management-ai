import pytest
from Spreadsheet import spreadsheet


class FakeWorksheet:
    """Google Sheetsの代わりに使用するテスト用シート"""

    def __init__(self, records=None):
        self.records = records or []
        self.appended_rows = []

    def get_all_records(self):
        return self.records

    def append_row(self, row):
        self.appended_rows.append(row)
        self.records.append({
            "user_id": row[0],
            "LINE表示名": row[1],
            "名前": row[2],
            "状態": row[3],
        })


@pytest.fixture
def fake_worksheet(monkeypatch):
    """テスト中は実際のGoogle Sheetsに接続しない"""
    worksheet = FakeWorksheet()

    monkeypatch.setattr(
        spreadsheet,
        "get_users_sheet",
        lambda: worksheet
    )

    return worksheet


# -----------------------------
# get_user_status() のテスト
# -----------------------------

def test_get_user_status_existing_user(fake_worksheet):
    """登録済みユーザーの状態を取得できる"""
    fake_worksheet.records.append({
        "user_id": "U001",
        "LINE表示名": "テストユーザー",
        "名前": "テスト",
        "状態": "有効",
    })

    result = spreadsheet.get_user_status("U001")

    assert result == "有効"


def test_get_user_status_unregistered_user(fake_worksheet):
    """未登録ユーザーの場合はNoneを返す"""
    result = spreadsheet.get_user_status("U999")

    assert result is None


def test_get_user_status_strips_whitespace(fake_worksheet):
    """IDの前後に空白があっても同じユーザーとして判定する"""
    fake_worksheet.records.append({
        "user_id": " U001 ",
        "LINE表示名": "テストユーザー",
        "名前": "テスト",
        "状態": " 有効 ",
    })

    result = spreadsheet.get_user_status("U001")

    assert result == "有効"


# -----------------------------
# register_user() のテスト
# -----------------------------

def test_register_user_success(fake_worksheet):
    """新規ユーザーを確認中として登録できる"""
    result = spreadsheet.register_user("U001", "テストユーザー")

    assert result is True
    assert len(fake_worksheet.appended_rows) == 1

    assert fake_worksheet.appended_rows[0] == [
        "U001",
        "テストユーザー",
        "",
        "確認中",
    ]


def test_register_user_duplicate(fake_worksheet):
    """登録済みユーザーを重複登録しない"""
    fake_worksheet.records.append({
        "user_id": "U001",
        "LINE表示名": "テストユーザー",
        "名前": "テスト",
        "状態": "有効",
    })

    result = spreadsheet.register_user("U001", "テストユーザー")

    assert result is False
    assert len(fake_worksheet.appended_rows) == 0


def test_register_user_duplicate_with_whitespace(fake_worksheet):
    """IDの前後に空白があっても重複登録しない"""
    fake_worksheet.records.append({
        "user_id": " U001 ",
        "LINE表示名": "テストユーザー",
        "名前": "テスト",
        "状態": "有効",
    })

    result = spreadsheet.register_user("U001", "テストユーザー")

    assert result is False
    assert len(fake_worksheet.appended_rows) == 0


# -----------------------------
# get_active_users() のテスト
# -----------------------------

def test_get_active_users(fake_worksheet):
    """有効ユーザーだけを取得できる"""

    fake_worksheet.records.extend([
        {
            "user_id": "U001",
            "LINE表示名": "ユーザー1",
            "名前": "田中",
            "状態": "有効",
        },
        {
            "user_id": "U002",
            "LINE表示名": "ユーザー2",
            "名前": "佐藤",
            "状態": "確認中",
        },
        {
            "user_id": "U003",
            "LINE表示名": "ユーザー3",
            "名前": "鈴木",
            "状態": "無効",
        },
    ])

    result = spreadsheet.get_active_users()

    assert len(result) == 1
    assert result[0]["user_id"] == "U001"


def test_get_active_users_excludes_pending(fake_worksheet):
    """確認中ユーザーを除外する"""

    fake_worksheet.records.extend([
        {
            "user_id": "U001",
            "LINE表示名": "ユーザー1",
            "名前": "田中",
            "状態": "確認中",
        },
    ])

    result = spreadsheet.get_active_users()

    assert result == []


def test_get_active_users_excludes_disabled(fake_worksheet):
    """無効ユーザーを除外する"""

    fake_worksheet.records.extend([
        {
            "user_id": "U001",
            "LINE表示名": "ユーザー1",
            "名前": "田中",
            "状態": "無効",
        },
    ])

    result = spreadsheet.get_active_users()

    assert result == []


def test_get_active_users_empty(fake_worksheet):
    """ユーザーがいない場合は空リストを返す"""

    result = spreadsheet.get_active_users()

    assert result == []