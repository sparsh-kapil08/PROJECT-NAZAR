import cv2
import numpy as np
from utils.roi_utils import extract_roi

def detect_artificial_light(frame):
    """
    Detect artificial light in room using multiple methods.
    
    Methods:
    1. Brightness analysis in ceiling ROI
    2. Light source detection (bright spots)
    3. Shadow analysis
    
    Returns:
        True if artificial light is strongly detected
    """
    roi = extract_roi(frame)
    
    if roi is None or roi.size == 0:
        return False
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Overall brightness in ceiling area
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    
    # STRICT: Increased threshold to reduce false positives
    brightness_threshold = 175  # Increased from 160
    _, bright_thresh = cv2.threshold(blurred, brightness_threshold, 255, cv2.THRESH_BINARY)
    
    bright_area = np.sum(bright_thresh == 255)
    total_area = bright_thresh.size
    glow_ratio = bright_area / total_area
    
    # Method 2: Detect light reflections/bright spots
    # Very bright pixels indicating light fixtures
    _, very_bright_mask = cv2.threshold(blurred, 220, 255, cv2.THRESH_BINARY)
    very_bright_ratio = np.sum(very_bright_mask == 255) / total_area
    
    # Method 3: Standard deviation analysis
    # Lit rooms have more varied brightness
    mean_brightness = np.mean(gray)
    brightness_std = np.std(gray)
    
    # Detect lights if:
    # - Bright areas present OR very bright spots detected
    # - AND ceiling is reasonably lit
    lights_detected = bool(
        (glow_ratio > 0.08 or very_bright_ratio > 0.02) and  # Stricter thresholds
        mean_brightness > 100  # Higher baseline brightness
    )
    
    return lights_detected

