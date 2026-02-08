import cv2
import time
import numpy as np
from ml_engine.detectors.water_detector import detect_raw_puddles
from ml_engine.detectors.person_detector import detect_person



CONFIRM_TIME = 180   # seconds
ALERT_COOLDOWN = 180

first_seen = None
last_alert = 0


def process_water_frame(frame):

    global first_seen, last_alert

    # 👤 Human present → ignore scene
    if detect_person(frame):
        first_seen = None
        return None, None

    _, puddles, mask = detect_raw_puddles(frame)

    area = sum(cv2.contourArea(c) for c in puddles)

    # no water visible
    if area < 250:
        first_seen = None
        return None, mask

    now = time.time()

    # start confirmation timer
    if first_seen is None:
        first_seen = now
        return None, mask

    # wait until confirmed stable
    if now - first_seen < CONFIRM_TIME:
        return None, mask

    # cooldown between alerts
    if now - last_alert < ALERT_COOLDOWN:
        return None, mask

    # severity
    if area > 1200:
        severity = "HIGH"
    elif area > 600:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    last_alert = now

    return {
        "issue": "WATER LEAK / SPILL",
        "severity": severity,
        "area": int(area),
        "confirmed_after_sec": int(now - first_seen)
    }, mask
