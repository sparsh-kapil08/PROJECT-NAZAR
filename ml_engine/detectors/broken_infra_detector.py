import cv2
import numpy as np
from ultralytics import YOLO

class BrokenInfrastructureDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

        # COCO class IDs
        self.CHAIR_CLASS_ID = 56
        self.TABLE_CLASS_ID = 60

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        broken_items = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            if conf < 0.4:
                continue

            if cls_id in [self.CHAIR_CLASS_ID, self.TABLE_CLASS_ID]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                roi = frame[y1:y2, x1:x2]

                if self._is_broken_shape(roi):
                    broken_items.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf
                    })

        return broken_items

    def _is_broken_shape(self, roi):
        if roi.size == 0:
            return False

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return False

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        x, y, w, h = cv2.boundingRect(largest)
        aspect_ratio = w / float(h + 1e-5)

        # Heuristic rules
        if area < 500:
            return False

        if aspect_ratio < 0.4 or aspect_ratio > 2.5:
            return True  # abnormal shape

        return False