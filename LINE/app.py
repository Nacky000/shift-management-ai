from flask import Flask, request, abort
# Flask：Webサーバー作るため，request：LINEから来たデータを受け取る，abort：エラーのとき通信を切る
from linebot import LineBotApi, WebhookHandler
# LineBotApi → 返信送る用，WebhookHandler → メッセージ処理の中枢
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# MessageEvent：メッセージ来たとき，TextMessage：テキストメッセージ，TextSendMessage：返信用メッセージ
from openai import OpenAI
# OpenAIを読み込む
import os
from dotenv import load_dotenv
# .envから秘密情報読む
from AI.ai_parser import chat

load_dotenv("../Config/.env") # .envの内容をPythonに読み込む

app = Flask(__name__) # Webサーバー本体
# クライアント作成（環境変数から取得）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
# これらは.envから読み込む，情報流出が防がれる

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
# LINE APIの初期化

@app.route("/webhook", methods=["POST"])

def webhook():
    # LINEがメッセージ送ってくるURL
    signature = request.headers.get("X-Line-Signature", "") # LINEから来た正規リクエストか確認する署名
    body = request.get_data(as_text=True) # メッセージ本体

    try:
        handler.handle(body, signature) # どの処理に回すかを判定する
    except InvalidSignatureError:
        abort(400) # 偽物リクエストを拒否する

    return "OK" # LINEに「受け取ったよ」と返す

@handler.add(MessageEvent, message=TextMessage) # 「テキストメッセージ来た時だけ実行
def handle_message(event):
    text = event.message.text # ユーザーの発言を取得
    print("受信:", text) # ターミナルに表示する（デバッグ用）

    try:
        response = client.responses.create(
            model="gpt-5.4-mini",
            instructions=SYSTEM_PROMPT,
            input=text
        )
        ai_text = response.output_text

    except Exception as e:
        print(e)
        ai_text = "エラーが発生しました"

    line_bot_api.reply_message( # LINEに返信する
        event.reply_token,
        TextSendMessage(text=ai_text)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) # サーバー起動