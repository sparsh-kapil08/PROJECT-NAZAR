from detectors.waste_detector import detect_waste


def process_waste_frame(frame):

    detected, boxes, mask, score = detect_waste(frame)

    if not detected:
        return None, mask

    severity = "LOW"
    if score > 18 or len(boxes) > 3:
        severity = "MEDIUM"
    if score > 28 or len(boxes) > 6:
        severity = "HIGH"

    return {
        "issue": "WASTE / CLUTTER DETECTED",
        "severity": severity,
        "clutter_score": round(score,2),
        "objects": len(boxes)
    }, mask
