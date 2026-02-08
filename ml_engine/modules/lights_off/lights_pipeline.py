from ml_engine.core.decision_engine import process_frame

class LightsOffSystem:
    def __init__(self):
        self.active = True

    def analyze_frame(self, frame):
        if not self.active:
            return None
        return process_frame(frame)
