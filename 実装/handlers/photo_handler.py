from flask import jsonify
from utils.aws_utils import upload_to_s3, save_to_dynamodb, analyze_photo_with_rekognition, get_photo_url_from_dynamodb, save_analysis_result
import uuid
from datetime import datetime
from decimal import Decimal

def upload_photo(participant_id, photo):
    try:
        # S3に写真をアップロード
        photo_id = str(uuid.uuid4())  # 任意のユニークID生成ロジックを使用
        s3_url = upload_to_s3(photo, photo_id)
        
        # DynamoDBに写真情報を保存
        photo_info = {
            'id': photo_id,  # プライマリキー
            'participant_id': participant_id,
            'url': s3_url,
            'uploaded_at': datetime.now().isoformat()
        }
        save_to_dynamodb('photos', photo_info)

        # Rekognitionで分析
        labels, scores = analyze_photo_with_rekognition(s3_url)
        if labels and scores:
            for label, score in zip(labels, scores):
                result_id = str(uuid.uuid4())
                save_analysis_result(result_id, photo_id, label, Decimal(score))  # スコアをDecimalとして渡す

        return jsonify({"message": "Photo uploaded and analyzed successfully", "photo_id": photo_id, "url": s3_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def save_analysis_result(result_id, photo_id, landmark_name, score):
    item = {
        'id': result_id,
        'photo_id': photo_id,
        'landmark_name': landmark_name,
        'score': score
    }
    save_to_dynamodb('analysis_results', item)