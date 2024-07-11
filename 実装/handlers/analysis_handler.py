from flask import jsonify
from utils.aws_utils import analyze_photo_with_rekognition, get_photo_url_from_dynamodb, save_analysis_result
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def analyze_photo(photo_id):
    photo_url = get_photo_url_from_dynamodb(photo_id)
    if not photo_url:
        return jsonify({'message': 'Photo not found'}), 404

    labels = analyze_photo_with_rekognition(photo_url)
    if not labels:
        return jsonify({'message': 'Rekognition analysis failed'}), 500

    result_id = photo_id  # 簡易的にphoto_idをresult_idとして使用

    for label in labels:
        save_analysis_result(result_id, photo_id, label['Name'], label['Confidence'])

    return jsonify({'message': 'Analysis successful', 'labels': labels}), 200