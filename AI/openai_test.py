from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 読み込み
load_dotenv("../Config/.env")

# クライアント作成（環境変数から取得）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# API呼び出し
response = client.responses.create(
    model="gpt-5.4-mini",
    input="write a haiku about ai",
    store=True
)

# 結果表示
print(response.output_text)