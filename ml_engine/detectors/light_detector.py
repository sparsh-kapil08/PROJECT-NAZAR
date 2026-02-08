import cv2
import numpy as np
from ml_engine.core.config import BRIGHTNESS_THRESHOLD
from ml_engine.utils.roi_utils import extract_roi

def detect_artificial_light(frame):
    roi = extract_roi(frame)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (7,7), 0)
    _, thresh = cv2.threshold(
        blurred, BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY
    )

    bright_area = np.sum(thresh == 255)
    total_area = thresh.size

    glow_ratio = bright_area / total_area

    return glow_ratio > 0.08
