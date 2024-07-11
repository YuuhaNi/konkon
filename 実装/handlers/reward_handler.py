from flask import jsonify
from utils.aws_utils import save_to_dynamodb, save_activity_log

def generate_reward(participant_id, score):
    reward = {
        'id': int(datetime.utcnow().timestamp()),
        'participant_id': participant_id,
        'score': score,
        'reward': determine_reward(score)
    }
    save_to_dynamodb('rewards', reward)
    save_activity_log(participant_id, f'Reward generated: {reward["reward"]}')
    return jsonify(reward)

def determine_reward(score):
    if score > 90:
        return 'Gold'
    elif score > 75:
        return 'Silver'
    else:
        return 'Bronze'