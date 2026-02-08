import cv2
import numpy as np

def detect_raw_puddles(frame):
    """Detect water puddles by looking for dark wet areas and blue/cyan hues"""
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 1. Detect blue/cyan water colors (H: 90-130, S: 50-255, V: 0-200)
    lower_blue = np.array([90, 50, 0])
    upper_blue = np.array([130, 255, 200])
    water_color_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # 2. Detect dark pixels (wet areas typically darker)
    # Wet floor is darker than dry floor
    dark_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)[1]
    
    # 3. Combine both masks - water is either blue-ish OR dark
    combined_mask = cv2.bitwise_or(water_color_mask, dark_mask)
    
    # Apply morphology to clean up noise
    kernel = np.ones((7, 7), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(
        combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    # Filter by area - minimum 200 pixels for water puddle
    puddles = [c for c in contours if cv2.contourArea(c) > 200]
    
    return frame, puddles, combined_mask
