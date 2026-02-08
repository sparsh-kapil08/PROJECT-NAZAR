"""
Broken Infrastructure Detector

Detects common infrastructure issues:
- Broken/cracked walls
- Faulty/hanging wires
- Damaged ceiling
- Broken windows/glass
- General damage/deterioration
"""

import cv2
import numpy as np


def detect_crack_patterns(frame):
    """Detect cracks and line patterns in infrastructure"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Edge detection to find cracks/lines
    edges = cv2.Canny(gray, 50, 150)
    
    # Detect lines (cracks often appear as lines)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, minLineLength=50, maxLineGap=10)
    
    crack_score = 0.0
    if lines is not None:
        crack_score = min(len(lines) / 20.0, 1.0)  # Normalize to 0-1
    
    return crack_score, edges


def detect_dark_areas(frame):
    """Detect dark/damaged areas that indicate deterioration"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Look for consistently dark areas (water stains, mold, damage)
    _, dark_mask = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    
    # Filter out very small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
    
    dark_percentage = np.count_nonzero(dark_mask) / dark_mask.size
    
    return dark_percentage


def detect_color_anomalies(frame):
    """Detect unusual colors indicating rust, staining, or deterioration"""
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Detect brown/rust colors (H: 10-20, S: 100-255, V: 50-200)
    lower_rust = np.array([10, 100, 50])
    upper_rust = np.array([20, 255, 200])
    rust_mask = cv2.inRange(hsv, lower_rust, upper_rust)
    
    # Detect orange/stain colors (H: 5-15, S: 100-255, V: 100-230)
    lower_stain = np.array([5, 100, 100])
    upper_stain = np.array([15, 255, 230])
    stain_mask = cv2.inRange(hsv, lower_stain, upper_stain)
    
    # Combine masks
    anomaly_mask = cv2.bitwise_or(rust_mask, stain_mask)
    
    # Filter noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    anomaly_mask = cv2.morphologyEx(anomaly_mask, cv2.MORPH_OPEN, kernel)
    
    anomaly_percentage = np.count_nonzero(anomaly_mask) / anomaly_mask.size
    
    return anomaly_percentage


def detect_texture_damage(frame):
    """Detect texture anomalies indicating peeling paint, potholes, etc."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate Laplacian variance (high variance = rough/damaged surface)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    variance = np.var(lap)
    
    # Normalize variance to 0-1 scale (empirically determined)
    # High variance (>1000) indicates significant texture damage
    damage_score = min(variance / 2000.0, 1.0)
    
    return damage_score


def detect_broken_infrastructure(frame):
    """
    Comprehensive broken infrastructure detection.
    
    Checks for:
    - Cracks in walls/ceiling
    - Dark stains/moisture/mold
    - Rust or color anomalies
    - Texture damage (peeling paint, deterioration)
    
    Returns:
        (is_broken, severity, details_dict)
    """
    
    # Calculate different damage indicators
    crack_score, edges = detect_crack_patterns(frame)
    dark_percentage = detect_dark_areas(frame)
    anomaly_percentage = detect_color_anomalies(frame)
    texture_damage = detect_texture_damage(frame)
    
    # Weighted score calculation
    # Higher weight on visual anomalies and cracks
    total_score = (
        crack_score * 0.3 +           # 30%: Crack patterns
        dark_percentage * 0.25 +      # 25%: Dark areas (mold, water damage)
        anomaly_percentage * 0.25 +   # 25%: Color anomalies (rust, stains)
        texture_damage * 0.2          # 20%: Texture damage
    )
    
    # Determine severity
    severity = "LOW"
    if total_score > 0.5:
        severity = "MEDIUM"
    if total_score > 0.7:
        severity = "HIGH"
    
    # STRICT: Infrastructure is broken only if score is HIGH (>0.50)
    # This prevents false positives from furniture, shadows, etc.
    is_broken = bool(total_score > 0.50)
    
    details = {
        "total_damage_score": float(total_score),  # Convert numpy float to Python float
        "crack_score": float(crack_score),
        "dark_areas_percentage": float(dark_percentage * 100),
        "color_anomalies_percentage": float(anomaly_percentage * 100),
        "texture_damage_score": float(texture_damage),
        "severity": severity
    }
    
    return is_broken, severity, details
