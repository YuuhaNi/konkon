from datetime import datetime

class Photo:
    def __init__(self, id, participant_id, url, uploaded_at):
        self.id = id
        self.participant_id = participant_id
        self.url = url
        self.uploaded_at = uploaded_at

    def get_photo_info(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'url': self.url,
            'uploaded_at': self.uploaded_at
        }
