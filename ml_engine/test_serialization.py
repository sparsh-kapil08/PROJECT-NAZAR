#!/usr/bin/env python3
"""
Test script to verify JSON serialization works correctly.
Run this before deploying to catch any numpy type issues.
"""

import json
import numpy as np
from detectors.infrastructure_detector import detect_broken_infrastructure
from detectors.light_detector import detect_artificial_light
from detectors.fan_motion_detector import detect_fan_motion
from detectors.person_detector import detect_person
from detectors.water_detector import detect_raw_puddles
from detectors.waste_detector import detect_waste
import cv2
import sys


def test_json_serialization(obj, detector_name):
    """Test if object can be serialized to JSON"""
    try:
        json_str = json.dumps(obj)
        print(f"✅ {detector_name}: JSON serialization OK")
        return True
    except TypeError as e:
        print(f"❌ {detector_name}: JSON serialization FAILED")
        print(f"   Error: {e}")
        print(f"   Object: {obj}")
        return False


def test_detectors(image_path):
    """Test all detectors for JSON serialization issues"""
    
    # Load image
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"❌ Failed to load image: {image_path}")
        sys.exit(1)
    
    print(f"📷 Testing image: {image_path}\n")
    
    results = {}
    
    # Test infrastructure detector
    print("[1] Testing Broken Infrastructure Detector...")
    try:
        is_broken, severity, details = detect_broken_infrastructure(frame)
        result = {
            "is_broken": is_broken,
            "severity": severity,
            "details": details
        }
        results["infrastructure"] = test_json_serialization(result, "Infrastructure")
    except Exception as e:
        print(f"❌ Infrastructure detector error: {e}")
        results["infrastructure"] = False
    
    # Test light detector
    print("\n[2] Testing Light Detector...")
    try:
        lights_on = detect_artificial_light(frame)
        result = {"lights_detected": lights_on}
        results["light"] = test_json_serialization(result, "Light")
    except Exception as e:
        print(f"❌ Light detector error: {e}")
        results["light"] = False
    
    # Test fan detector
    print("\n[3] Testing Fan Motion Detector...")
    try:
        fan_on = detect_fan_motion(frame)
        result = {"fan_detected": fan_on}
        results["fan"] = test_json_serialization(result, "Fan")
    except Exception as e:
        print(f"❌ Fan detector error: {e}")
        results["fan"] = False
    
    # Test person detector
    print("\n[4] Testing Person Detector...")
    try:
        person_detected = detect_person(frame)
        result = {"person_detected": person_detected}
        results["person"] = test_json_serialization(result, "Person")
    except Exception as e:
        print(f"❌ Person detector error: {e}")
        results["person"] = False
    
    # Test water detector
    print("\n[5] Testing Water Detector...")
    try:
        _, puddles, mask = detect_raw_puddles(frame)
        area = sum(cv2.contourArea(c) for c in puddles)
        result = {
            "puddles": len(puddles),
            "area": area,
            "water_detected": area > 250
        }
        results["water"] = test_json_serialization(result, "Water")
    except Exception as e:
        print(f"❌ Water detector error: {e}")
        results["water"] = False
    
    # Test waste detector
    print("\n[6] Testing Waste Detector...")
    try:
        detected, boxes, _, score = detect_waste(frame)
        result = {
            "waste_detected": detected,
            "objects": len(boxes),
            "clutter_score": score
        }
        results["waste"] = test_json_serialization(result, "Waste")
    except Exception as e:
        print(f"❌ Waste detector error: {e}")
        results["waste"] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for detector, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{detector:15} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All detectors are JSON serializable!")
        return True
    else:
        print(f"\n⚠️  {total - passed} detector(s) have serialization issues")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_serialization.py <image_path>")
        print("Example: python test_serialization.py sample.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = test_detectors(image_path)
    sys.exit(0 if success else 1)
