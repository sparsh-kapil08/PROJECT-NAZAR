import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO

# MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    smooth_landmarks=False
)

# YOLOv8 for person detection (more reliable backup)
yolo_model = YOLO("yolov8n.pt")

def detect_person_mediapipe(frame):
    """Detect person using MediaPipe pose estimation"""
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)
        return result.pose_landmarks is not None
    except Exception as e:
        print(f"MediaPipe error: {e}")
        return False

def detect_person_yolo(frame):
    """Detect person using YOLO object detection"""
    try:
        results = yolo_model(frame, conf=0.4)[0]
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = yolo_model.names[class_id]
            if class_name == "person":
                return True
        return False
    except Exception as e:
        print(f"YOLO error: {e}")
        return False

def detect_person(frame):
    """
    Detect person using multiple methods for higher reliability.
    Uses both MediaPipe pose and YOLO detection.
    
    Returns:
        True if a person is detected by either method
    """
    # Try both detection methods
    pose_detected = detect_person_mediapipe(frame)
    person_detected = detect_person_yolo(frame)
    
    # Return True if either method detects a person
    # YOLO is more reliable for full-body detection
    # MediaPipe is better for pose/movement
    return person_detected or pose_detected
