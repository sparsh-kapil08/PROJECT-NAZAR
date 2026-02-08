"""
Individual detector test module.
Run individual detectors on test images to verify correctness.

Usage:
    python test_detectors.py <image_path> [--detector water|waste|person|light|fan|all]
"""

import cv2
import sys
import argparse
from detectors.water_detector import detect_raw_puddles
from detectors.waste_detector import detect_waste
from detectors.person_detector import detect_person, detect_person_mediapipe, detect_person_yolo
from detectors.light_detector import detect_artificial_light
from detectors.fan_motion_detector import detect_fan_motion
from detectors.infrastructure_detector import detect_broken_infrastructure


def test_water_detection(frame, image_path):
    """Test water leak detection"""
    print("\n[WATER DETECTOR TEST]")
    try:
        _, puddles, mask = detect_raw_puddles(frame)
        area = sum(cv2.contourArea(c) for c in puddles)
        
        print(f"  ✓ Puddles detected: {len(puddles)}")
        print(f"  ✓ Total puddle area: {area} pixels")
        print(f"  ✓ Water detected: {'YES' if area > 250 else 'NO'}")
        
        return {
            "status": "SUCCESS",
            "puddles_count": len(puddles),
            "puddle_area": area,
            "water_detected": area > 250
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "ERROR", "error": str(e)}


def test_waste_detection(frame, image_path):
    """Test waste/clutter detection"""
    print("\n[WASTE DETECTOR TEST]")
    try:
        detected, boxes, _, score = detect_waste(frame)
        
        print(f"  ✓ Trash objects detected: {len(boxes)}")
        print(f"  ✓ Clutter score: {score:.2f}")
        print(f"  ✓ Waste detected: {'YES' if detected else 'NO'}")
        
        return {
            "status": "SUCCESS",
            "objects_detected": len(boxes),
            "clutter_score": score,
            "waste_detected": detected
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "ERROR", "error": str(e)}


def test_person_detection(frame, image_path):
    """Test person/unauthorized access detection"""
    print("\n[PERSON DETECTOR TEST]")
    try:
        person_detected = detect_person(frame)
        
        print(f"  ✓ Person detected: {'YES' if person_detected else 'NO'}")
        
        # Show detection method details
        pose_detected = detect_person_mediapipe(frame)
        yolo_detected = detect_person_yolo(frame)
        
        print(f"    - MediaPipe pose: {'YES' if pose_detected else 'NO'}")
        print(f"    - YOLO person: {'YES' if yolo_detected else 'NO'}")
        
        return {
            "status": "SUCCESS",
            "person_detected": person_detected,
            "mediapipe_detected": pose_detected,
            "yolo_detected": yolo_detected
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "ERROR", "error": str(e)}


def test_light_detection(frame, image_path):
    """Test artificial light detection"""
    print("\n[LIGHT DETECTOR TEST]")
    try:
        lights_on = detect_artificial_light(frame)
        
        print(f"  ✓ Artificial lights detected: {'YES' if lights_on else 'NO'}")
        
        return {
            "status": "SUCCESS",
            "lights_detected": lights_on
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "ERROR", "error": str(e)}


def test_fan_detection(frame, image_path):
    """Test fan motion detection"""
    print("\n[FAN MOTION DETECTOR TEST]")
    try:
        fan_detected = detect_fan_motion(frame)
        
        print(f"  ✓ Fan motion detected: {'YES' if fan_detected else 'NO'}")
        
        return {
            "status": "SUCCESS",
            "fan_motion_detected": fan_detected
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "ERROR", "error": str(e)}


def test_infrastructure_detection(frame, image_path):
    """Test broken infrastructure detection"""
    print("\n[INFRASTRUCTURE DETECTOR TEST]")
    try:
        is_broken, severity, details = detect_broken_infrastructure(frame)
        
        print(f"  ✓ Infrastructure broken: {'YES' if is_broken else 'NO'}")
        print(f"  ✓ Severity: {severity}")
        print(f"  ✓ Damage score: {details['total_damage_score']}")
        print(f"    - Crack score: {details['crack_score']}")
        print(f"    - Dark areas: {details['dark_areas_percentage']}%")
        print(f"    - Color anomalies: {details['color_anomalies_percentage']}%")
        print(f"    - Texture damage: {details['texture_damage_score']}")
        
        return {
            "status": "SUCCESS",
            "infrastructure_broken": is_broken,
            "severity": severity,
            "details": details
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"status": "ERROR", "error": str(e)}


def test_all_detectors(frame, image_path):
    """Run all detectors and show results"""
    print("\n" + "="*60)
    print("RUNNING ALL DETECTORS")
    print("="*60)
    
    results = {}
    results["water"] = test_water_detection(frame, image_path)
    results["waste"] = test_waste_detection(frame, image_path)
    results["person"] = test_person_detection(frame, image_path)
    results["light"] = test_light_detection(frame, image_path)
    results["fan"] = test_fan_detection(frame, image_path)
    results["infrastructure"] = test_infrastructure_detection(frame, image_path)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Test individual ML detectors on an image"
    )
    parser.add_argument("image_path", help="Path to test image")
    parser.add_argument(
        "--detector",
        default="all",
        choices=["water", "waste", "person", "light", "fan", "infrastructure", "all"],
        help="Which detector to test (default: all)"
    )
    
    args = parser.parse_args()
    
    # Load image
    frame = cv2.imread(args.image_path)
    if frame is None:
        print(f"✗ Failed to load image: {args.image_path}")
        sys.exit(1)
    
    print(f"\n📷 Testing image: {args.image_path}")
    print(f"   Dimensions: {frame.shape}")
    
    # Run tests
    if args.detector == "all":
        results = test_all_detectors(frame, args.image_path)
    elif args.detector == "water":
        results = test_water_detection(frame, args.image_path)
    elif args.detector == "waste":
        results = test_waste_detection(frame, args.image_path)
    elif args.detector == "person":
        results = test_person_detection(frame, args.image_path)
    elif args.detector == "light":
        results = test_light_detection(frame, args.image_path)
    elif args.detector == "fan":
        results = test_fan_detection(frame, args.image_path)
    elif args.detector == "infrastructure":
        results = test_infrastructure_detection(frame, args.image_path)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    if isinstance(results, dict) and "status" in results:
        print(f"Status: {results['status']}")
        for key, value in results.items():
            if key != "status":
                print(f"  {key}: {value}")
    else:
        for detector, result in results.items():
            print(f"\n{detector.upper()}:")
            print(f"  Status: {result.get('status', 'UNKNOWN')}")
            for key, value in result.items():
                if key != "status":
                    print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
