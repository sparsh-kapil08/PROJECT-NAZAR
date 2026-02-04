import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose.Pose()

def detect_person(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = mp_pose.process(rgb)
    return result.pose_landmarks is not None
