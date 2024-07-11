from utils.aws_utils import save_to_dynamodb

def save_participant(participant_id, name, email, qr_code):
    item = {
        'id': participant_id,
        'name': name,
        'email': email,
        'qr_code': qr_code
    }
    save_to_dynamodb('participants', item)