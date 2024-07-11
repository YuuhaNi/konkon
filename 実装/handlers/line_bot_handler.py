import os
import logging
import random
from datetime import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from utils.aws_utils import upload_to_s3, save_to_dynamodb, analyze_photo_with_rekognition, save_analysis_result, generate_unique_id

# 環境変数の取得
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_line_bot_event(event):
    try:
        signature = event['headers'].get('X-Line-Signature', '')
        body = event['body']
        handler.handle(body, signature)
        return {"message": "Success"}
    except InvalidSignatureError:
        return {"message": "Invalid Signature"}, 400
    except Exception as e:
        logger.error(f"イベント処理中にエラーが発生しました: {str(e)}")
        return {"message": "Internal Server Error"}, 500

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='こんにちは!')
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    try:
        # 画像のバイナリデータを取得
        message_content = line_bot_api.get_message_content(event.message.id)

        # 画像を一時ファイルに保存
        temp_file_path = f"/tmp/{event.message.id}.jpg"
        with open(temp_file_path, 'wb') as temp_file:
            for chunk in message_content.iter_content():
                temp_file.write(chunk)

        # S3にアップロード
        s3_url = upload_to_s3(temp_file_path, event.message.id)
        logger.info(f"Image uploaded to S3: {s3_url}")

        # データベースに保存
        photo_info = {
            'id': int(event.message.id),  # プライマリキー
            'participant_id': event.source.user_id,  # LINEのユーザーIDを使用
            'url': s3_url,
            'uploaded_at': datetime.now().isoformat()
        }
        save_to_dynamodb('photos', photo_info)
        logger.info(f"Photo info saved to DynamoDB: {photo_info}")

        # Rekognitionで画像分析
        labels, scores = analyze_photo_with_rekognition(s3_url)
        logger.info(f"Labels detected by Rekognition: {labels}")
        logger.info(f"Scores detected by Rekognition: {scores}")

        # 分析結果の中から最も高いスコアのラベルとスコアを保存
        if labels and scores:
            top_label = labels[0]
            top_score = scores[0]
            result_id = generate_unique_id()
            save_analysis_result(result_id, int(event.message.id), top_label, top_score)

        # 応答メッセージを送信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"画像を受け取りました。検出されたラベル: {labels[0]}")
        )
    except Exception as e:
        logger.error(f"画像の処理中にエラーが発生しました: {str(e)}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="画像の処理中にエラーが発生しました。")
        )

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)