from detectors.waste_detector import detect_waste


def process_waste_frame(frame, water_mask=None):
    """
    Process frame for waste/clutter detection.
    
    Args:
        frame: Input frame
        water_mask: Optional mask for water regions to exclude from analysis
    """
    detected, boxes, mask, score = detect_waste(frame, water_mask)

    if not detected:
        return None, mask

    severity = "LOW"
    if score > 30 or len(boxes) > 5:
        severity = "MEDIUM"
    if score > 40 or len(boxes) > 10:
        severity = "HIGH"

    return {
        "status": "ISSUE_DETECTED",
        "issue_type": "Waste / Clutter",
        "severity": severity,
        "details": {
            "clutter_score": round(score, 2),
            "objects_detected": len(boxes)
        }
    }, mask