import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

TRASH_CLASSES = [
    "bottle", "cup", "wine glass", "plastic bag",
    "banana", "apple", "sandwich", "fork", "spoon"
]


def yolo_trash(frame):
    results = model(frame, conf=0.3)[0]

    boxes = []
    for b in results.boxes:
        name = model.names[int(b.cls[0])]
        if name in TRASH_CLASSES:
            boxes.append(tuple(map(int, b.xyxy[0])))

    return boxes


def clutter_score(frame):

    h, w, _ = frame.shape
    roi = frame[int(h*0.55):h, :]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 70, 140)
    edge_ratio = edges.mean() / 255

    lap = cv2.Laplacian(gray, cv2.CV_64F)
    texture = np.var(lap)

    score = edge_ratio * texture

    mask = np.zeros_like(gray)
    mask[edges > 0] = 255

    return score, mask


def detect_waste(frame):

    trash_boxes = yolo_trash(frame)
    score, mask = clutter_score(frame)

    clutter_detected = score > 12

    waste_detected = bool(trash_boxes) or clutter_detected

    return waste_detected, trash_boxes, mask, score
