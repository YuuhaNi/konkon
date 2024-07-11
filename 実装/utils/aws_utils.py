import boto3
import logging
from datetime import datetime
from decimal import Decimal
import random

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def upload_to_s3(file_path, file_name):
    s3 = boto3.client('s3')
    bucket_name = 'gpt-konkon-project-bucket'
    key = f'photos/{file_name}.jpg'
    try:
        with open(file_path, 'rb') as file:
            s3.upload_fileobj(file, bucket_name, key)
        url = f'https://{bucket_name}.s3.amazonaws.com/{key}'
        logger.info(f"Image uploaded to S3: {url}")
        return url
    except Exception as e:
        logger.error(f"S3へのアップロードに失敗しました: {str(e)}")
        raise

def save_to_dynamodb(table_name, item):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    try:
        table.put_item(Item=item)
        logger.info(f"Item saved to DynamoDB table {table_name}: {item}")
    except Exception as e:
        logger.error(f"DynamoDBへの保存に失敗しました: {str(e)}")
        raise

def save_participant(participant_id, name, email, qr_code):
    item = {
        'id': participant_id,
        'name': name,
        'email': email,
        'qr_code': qr_code
    }
    save_to_dynamodb('participants', item)

def generate_unique_id():
    return int(datetime.now().timestamp() * 1000) + random.randint(0, 1000)

def save_analysis_result(result_id, photo_id, label, score):
    item = {
        'id': result_id,  # idを整数型に変更
        'photo_id': photo_id,
        'landmark_name': label,
        'score': Decimal(str(score))  # スコアをDecimalに変換
    }
    logger.info(f"Saving analysis result item: {item}")
    save_to_dynamodb('analysis_results', item)

def save_activity_log(log_id, participant_id, action):
    item = {
        'id': log_id,
        'participant_id': participant_id,
        'action': action,
        'executed_at': datetime.utcnow().isoformat()
    }
    save_to_dynamodb('activity_logs', item)

def get_photo_url_from_dynamodb(photo_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('photos')
    try:
        response = table.get_item(Key={'id': photo_id})
        return response['Item']['url'] if 'Item' in response else None
    except Exception as e:
        logger.error(f"DynamoDBからの写真URL取得に失敗しました: {str(e)}")
        return None

def analyze_photo_with_rekognition(photo_url):
    rekognition = boto3.client('rekognition')
    bucket_name = 'gpt-konkon-project-bucket'
    key = photo_url.split(f'https://{bucket_name}.s3.amazonaws.com/')[1]  # オブジェクトキーを抽出

    try:
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket_name, 'Name': key}},
            MaxLabels=10
        )
        labels = [label['Name'] for label in response['Labels']]
        scores = [label['Confidence'] for label in response['Labels']]
        logger.info(f"Labels detected by Rekognition: {labels}")
        logger.info(f"Scores detected by Rekognition: {scores}")
        return labels, scores
    except Exception as e:
        logger.error(f"Rekognitionのラベル検出に失敗しました: {str(e)}", exc_info=True)
        return None, None

def process_and_save_photo(photo_url, photo_id):
    labels, scores = analyze_photo_with_rekognition(photo_url)
    if labels and scores:
        # ユニークIDをタイムスタンプとランダムな整数で生成
        result_id = generate_unique_id()
        # 最も高いスコアのラベルとスコアを保存
        top_label = labels[0]
        top_score = scores[0]
        save_analysis_result(result_id, photo_id, top_label, top_score)
    else:
        logger.error("No labels or scores detected.")