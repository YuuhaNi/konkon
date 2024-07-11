import uuid
from flask import jsonify
from utils.aws_utils import save_activity_log

def log_activity(participant_id, action):
    try:
        log_id = generate_unique_id()
        save_activity_log(log_id, participant_id, action)
        return jsonify({"message": "Activity logged successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error logging activity", "error": str(e)}), 500

def generate_unique_id():
    return str(uuid.uuid4())