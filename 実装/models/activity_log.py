from datetime import datetime

class ActivityLog:
    def __init__(self, id, participant_id, action, executed_at):
        self.id = id
        self.participant_id = participant_id
        self.action = action
        self.executed_at = executed_at

    def get_log_info(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'action': self.action,
            'executed_at': self.executed_at.strftime('%Y-%m-%d %H:%M:%S')  # 修正: datetimeを文字列に変換してシリアライズ
        }