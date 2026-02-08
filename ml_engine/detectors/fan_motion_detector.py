import cv2
import numpy as np
from utils.roi_utils import extract_roi

prev_frame = None

def detect_fan_motion(frame):
    global prev_frame

    roi = extract_roi(frame)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    if prev_frame is None:
        prev_frame = gray
        return False

    diff = cv2.absdiff(prev_frame, gray)
    motion_score = np.mean(diff)

    prev_frame = gray

    return motion_score > 25
