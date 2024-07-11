class AnalysisResult:
    def __init__(self, id, photo_id, landmark_name, score):
        self.id = id
        self.photo_id = photo_id
        self.landmark_name = landmark_name
        self.score = score

    def get_analysis_info(self):
        return {
            'id': self.id,
            'photo_id': self.photo_id,
            'landmark_name': self.landmark_name,
            'score': self.score
        }
