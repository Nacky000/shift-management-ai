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
# from AI.ai_parser import chat
from Spreadsheet import spreadsheet

from AI import ai_parser
from AI import dispatcher

load_dotenv("../Config/.env") # .envの内容をPythonに読み込む

app = Flask(__name__) # Webサーバー本体
# クライアント作成（環境変数から取得）
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    # 1. LINE からメッセージと「user_id」を取得する
    user_id = event.source.user_id
    text = event.message.text
    print(f"受信 [User: {user_id}]: {text}") # デバッグ用にIDも表示

    try:
        # 登録状態を確認
        status = spreadsheet.get_user_status(user_id)

        # 未登録ならLINEプロフィールを取得して登録
        if status is None:
            try:
                profile = line_bot_api.get_profile(user_id)
                line_name = profile.display_name
            except Exception as e:
                print("LINEプロフィール取得エラー:", e)
                line_name = "取得できませんでした"

            spreadsheet.register_user(user_id, line_name)

            # 登録直後は確認中として扱う
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=(
                        "初回登録を受け付けました！\n"
                        "現在、店長の確認待ちです。\n"
                        "有効化されるとシフト登録を利用できます。"
                    )
                )
            )
            return

        # 状態に応じて利用可否を判定
        if status == "確認中":
            reply_text = (
                "現在、店長の確認待ちです。\n"
                "有効化されるまでお待ちください。"
            )

        elif status == "無効":
            reply_text = (
                "現在、このアカウントは利用できません。\n"
                "店長にお問い合わせください。"
            )

        elif status != "有効":
            reply_text = (
                "アカウントの状態を確認できません。\n"
                "店長にお問い合わせください。"
            )
        # response = client.responses.create(
        #     model="gpt-5.4-mini",
        #     instructions=SYSTEM_PROMPT,
        #     input=text
        # )
        # ai_text = response.output_text

        # ai_parser.py を呼び出して自由記述を構造化（JSON化）する
        else:
            parsed_json = ai_parser.parse_message(text)
            print("AI解析結果:", parsed_json)

            # dispatcher.py に user_id と 解析結果のJSON を渡して各ハンドラーへルーティング
            ai_text = dispatcher.dispatch_tasks(user_id, parsed_json)
            reply_text = ai_text

    except Exception as e:
        print("エラー発生:", e)
        reply_text = "処理中にエラーが発生しました．もう一度お試しいただくか，管理者にお問い合わせください．"

    line_bot_api.reply_message( # LINEに返信する
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) # サーバー起動