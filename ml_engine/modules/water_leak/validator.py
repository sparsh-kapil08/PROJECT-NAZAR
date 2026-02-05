import cv2
import numpy as np


def reject_false_positive(contour, roi):

    x, y, w, h = cv2.boundingRect(contour)
    area = cv2.contourArea(contour)

    # ---------------- HUMAN BLOCK ----------------
    # Humans appear tall compared to puddles
    if h > 140:
        return True

    # Leg/body like proportions
    ratio = h / (w + 1)
    if ratio > 2.5:
        return True


    # ---------------- SUNLIGHT / WALL GLARE BLOCK ----------------
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [contour], -1, 255, -1)

    mean_brightness = np.mean(gray[mask == 255])

    # Very bright = likely sunlight reflection, not puddle
    if mean_brightness > 235:
        return True


    # ---------------- SMALL NOISE ----------------
    if area < 250:
        return True


    return False
