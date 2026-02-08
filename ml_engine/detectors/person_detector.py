import cv2
from mediapipe.solutions import pose as mp_pose

pose = mp_pose.Pose()

def detect_person(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)
    return result.pose_landmarks is not None
