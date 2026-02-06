import cv2
import numpy as np
from detectors.water_detector import detect_raw_puddles
from detectors.person_detector import detect_person


area_buffer = []

def process_water_frame(frame):

    # 🚫 only strict rule: ignore humans
    if detect_person(frame):

        area_buffer.clear()
        return None, None

    _, puddles, mask = detect_raw_puddles(frame)

    area = sum(cv2.contourArea(c) for c in puddles)

    area_buffer.append(area)
    if len(area_buffer) > 10:
        area_buffer.pop(0)

    if len(area_buffer) < 4:
        return None, mask

    avg = np.mean(area_buffer)

    # loose boundary — ensures leaks always pass
    if avg < 250:
        return None, mask

    severity = "LOW"
    if avg > 1200:
        severity = "HIGH"
    elif avg > 600:
        severity = "MEDIUM"

    return {
        "issue": "WATER LEAK / SPILL",
        "severity": severity,
        "area": int(avg)
    }, mask


def reset_state():
    global buffer, _prev_gray
    buffer = []
    _prev_gray = None
