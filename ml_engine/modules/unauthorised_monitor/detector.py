import cv2
import os
import mediapipe as mp
from datetime import datetime

mp_pose = mp.solutions.pose

CAPTURE_DIR = "captures/unauthorized"
os.makedirs(CAPTURE_DIR, exist_ok=True)


class UnauthorizedDetector:
    def __init__(self):
        self.pose = mp_pose.Pose(static_image_mode=True)

    def is_restricted_time(self, start_hour: int, end_hour: int) -> bool:
        """
        Returns True if current time is outside the permitted access window
        """
        current_hour = datetime.now().hour

        if start_hour <= end_hour:
            return not (start_hour <= current_hour < end_hour)
        else:
            # Handles overnight windows like 22 → 6
            return not (current_hour >= start_hour or current_hour < end_hour)

    def detect_person(self, frame) -> bool:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        return results.pose_landmarks is not None

    def process_frame(self, frame, start_hour: int, end_hour: int):
        if not self.detect_person(frame):
            return {
                "unauthorized": False,
                "reason": "No person detected"
            }

        if not self.is_restricted_time(start_hour, end_hour):
            return {
                "unauthorized": False,
                "reason": "Person detected within permitted hours"
            }

        timestamp = datetime.now()
        filename = f"unauthorized_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        path = os.path.join(CAPTURE_DIR, filename)

        cv2.imwrite(path, frame)

        return {
            "unauthorized": True,
            "reason": "Unauthorized room usage detected",
            "timestamp": timestamp.isoformat(),
            "current_hour": timestamp.hour,
            "permitted_hours": f"{start_hour}:00–{end_hour}:00",
            "image_path": path
        }


detector = UnauthorizedDetector()