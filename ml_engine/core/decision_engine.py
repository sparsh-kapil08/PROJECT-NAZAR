"""
Decision Engine for infrastructure analysis.

Analyzes a single frame for:
1. Energy waste (lights, fans)
2. Broken infrastructure (cracks, damage)
3. General maintenance issues
"""

from detectors.light_detector import detect_artificial_light
from detectors.fan_motion_detector import detect_fan_motion
from detectors.infrastructure_detector import detect_broken_infrastructure


def process_frame(frame):
    """
    Analyze frame for infrastructure issues.
    
    For single image analysis, we don't rely on temporal tracking.
    Instead, we directly analyze what's visible in the frame.
    
    Returns:
        Dictionary with detected issues, or None if no issues found
    """
    
    issues = {}
    
    # ====== ENERGY WASTE DETECTION ======
    lights_on = detect_artificial_light(frame)
    fan_on = detect_fan_motion(frame)
    
    if lights_on or fan_on:
        issues["energy_waste"] = {
            "status": "DETECTED",
            "issue_type": "Energy Waste",
            "severity": "Medium",
            "details": {
                "lights_on": lights_on,
                "fan_running": fan_on
            }
        }
    
    # ====== BROKEN INFRASTRUCTURE DETECTION ======
    is_broken, severity, details = detect_broken_infrastructure(frame)
    
    if is_broken:
        issues["broken_infrastructure"] = {
            "status": "DETECTED",
            "issue_type": "Broken Infrastructure",
            "severity": severity,
            "details": details
        }
    
    # Return all detected issues, or None if nothing found
    return issues if issues else None

