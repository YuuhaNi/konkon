from flask import Flask, request, jsonify
from handlers.line_bot_handler import handle_line_bot_event, handler
from handlers.photo_handler import upload_photo
from handlers.analysis_handler import analyze_photo
from handlers.activity_handler import log_activity
from handlers.reward_handler import generate_reward
from dotenv import load_dotenv
from linebot.exceptions import InvalidSignatureError
import os
import boto3

# .envファイルのパスを明示的に指定
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# .envファイルの読み込み
load_dotenv(dotenv_path)

app = Flask(__name__)

# 環境変数の取得
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# 環境変数の確認（デバッグ用）
print("LINE_CHANNEL_ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
print("LINE_CHANNEL_SECRET:", LINE_CHANNEL_SECRET)

@app.route('/', methods=['GET'])
def index():
    return "Hello, this is the root endpoint of the Konkon project!"

@app.route('/linebot', methods=['POST'])
def linebot():
    print("Request headers:", request.headers)  # ログ出力の追加
    print("Request body:", request.get_data(as_text=True))  # ログ出力の追加

    # 署名検証
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return jsonify({'message': 'Invalid signature'}), 400

    return jsonify({'message': 'Success'}), 200

@app.route('/upload_photo', methods=['POST'])
def upload():
    participant_id = request.form['participant_id']
    photo = request.files['photo']
    return upload_photo(participant_id, photo)

@app.route('/analyze_photo', methods=['POST'])
def analyze():
    photo_id = request.form['photo_id']
    return analyze_photo(photo_id)

@app.route('/log_activity', methods=['POST'])
def log_activity_route():
    participant_id = request.form['participant_id']
    action = request.form['action']
    return log_activity(participant_id, action)

@app.route('/generate_reward', methods=['POST'])
def reward():
    participant_id = request.form['participant_id']
    score = request.form['score']
    return generate_reward(participant_id, score)

@app.route('/test_dynamodb', methods=['GET'])
def test_dynamodb():
    dynamodb = boto3.resource('dynamodb')
    table_name = 'participants'
    table = dynamodb.Table(table_name)

    try:
        response = table.scan()
        return jsonify({"message": "DynamoDB接続成功", "data": response})
    except Exception as e:
        return jsonify({"message": "DynamoDB接続失敗", "error": str(e)})

@app.route('/test_s3', methods=['GET'])
def test_s3():
    s3 = boto3.client('s3')
    bucket_name = 'konkon-project-bucket'

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        return jsonify({"message": "S3接続成功", "data": response})
    except Exception as e:
        return jsonify({"message": "S3接続失敗", "error": str(e)})

@app.route('/test_rekognition', methods=['GET'])
def test_rekognition():
    rekognition = boto3.client('rekognition')

    try:
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': 'konkon-project-bucket',
                    'Name': 'test-image.jpg'
                }
            },
            MaxLabels=10
        )
        return jsonify({"message": "Rekognition接続成功", "data": response})
    except Exception as e:
        return jsonify({"message": "Rekognition接続失敗", "error": str(e)})

if __name__ == '__main__':
    app.run()