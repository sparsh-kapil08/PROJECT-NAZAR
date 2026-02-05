import cv2
import numpy as np

def detect_raw_puddles(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # much looser brightness threshold
    _, mask = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)

    kernel = np.ones((7,7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # very loose area filter
    puddles = [c for c in contours if cv2.contourArea(c) > 150]

    return frame, puddles, mask
