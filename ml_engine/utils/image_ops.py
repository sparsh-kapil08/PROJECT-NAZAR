import cv2
import numpy as np

def to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def blur(img, k=7):
    return cv2.GaussianBlur(img, (k, k), 0)

def normalize(img):
    return cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)

def threshold(img, val):
    _, t = cv2.threshold(img, val, 255, cv2.THRESH_BINARY)
    return t

def frame_difference(f1, f2):
    return cv2.absdiff(f1, f2)

def contour_area(binary_img):
    contours, _ = cv2.findContours(
        binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    return sum(cv2.contourArea(c) for c in contours)

def brightness_score(gray):
    return np.mean(gray)
