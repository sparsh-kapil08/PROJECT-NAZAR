import cv2
import numpy as np
from utils.roi_utils import extract_roi

prev_frame = None
prev_frame_shape = None
consistent_motion_count = 0

def detect_fan_motion(frame):
    """
    Detect fan motion in ceiling ROI.
    
    For single image analysis, uses pattern detection:
    - Motion blur patterns
    - Circular/radial patterns (fan propeller)
    - Temporal consistency (if multiple frames available)
    
    Returns:
        True if fan motion is detected
    """
    global prev_frame, prev_frame_shape, consistent_motion_count
    
    roi = extract_roi(frame)
    
    if roi is None or roi.size == 0:
        return False
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Detect motion blur patterns
    # Fans create streaking/blur patterns
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    blur_variance = np.var(laplacian)
    
    # Method 2: Detect circular/radial patterns (propeller blades)
    # Use Hough circle detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=30,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=100
    )
    
    has_circular_pattern = circles is not None and len(circles[0]) > 0
    
    # Method 3: Compare with previous frame if available
    motion_detected_temporal = False
    if prev_frame is not None and prev_frame.shape == gray.shape:
        diff = cv2.absdiff(prev_frame, gray)
        motion_score = np.mean(diff)
        # Lowered threshold for better detection
        motion_detected_temporal = motion_score > 15
    
    # Update frame buffer
    prev_frame = gray.copy()
    prev_frame_shape = gray.shape
    
    # Fan is detected if:
    # - High motion blur variance OR
    # - Circular patterns detected OR
    # - Temporal motion detected
    
    fan_threshold = 500  # INCREASED from 300 - much stricter
    motion_detected = bool(
        blur_variance > fan_threshold or
        has_circular_pattern or
        (motion_detected_temporal and blur_variance > 200)  # Require motion blur confirmation
    )
    
    return motion_detected

