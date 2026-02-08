"""
Comprehensive ML Engine test suite.
Tests each detector independently and validates the conflict resolution system.

Usage:
    python test_ml_engine.py <image_path> [--verbose]
"""

import sys
import cv2
import argparse
from detectors.water_detector import detect_raw_puddles
from detectors.waste_detector import detect_waste
from detectors.person_detector import detect_person, detect_person_mediapipe, detect_person_yolo
from detectors.light_detector import detect_artificial_light
from detectors.fan_motion_detector import detect_fan_motion
from detectors.infrastructure_detector import detect_broken_infrastructure
from modules.water_leak.leak_pipeline import process_water_frame
from modules.waste_monitor.waste_pipeline import process_waste_frame


def test_pipeline(frame, verbose=False):
    """
    Run the full pipeline with independent detector validation.
    Shows raw results and conflict resolution.
    """
    
    print("\n" + "="*80)
    print("ML ENGINE PIPELINE TEST")
    print("="*80)
    
    results = {
        "raw_detections": {},
        "verified_detections": {},
        "conflicts": []
    }
    
    # ========== DETECTOR 1: WATER LEAK ==========
    print("\n[1/4] WATER LEAK DETECTION")
    print("-" * 80)
    try:
        water_result, water_mask = process_water_frame(frame)
        raw_puddles, puddles, _ = detect_raw_puddles(frame)
        puddle_area = sum(cv2.contourArea(c) for c in puddles)
        
        results["raw_detections"]["water"] = {
            "detected": bool(water_result),
            "puddles": len(puddles),
            "area": puddle_area,
            "status": water_result
        }
        
        print(f"  Puddles found: {len(puddles)}")
        print(f"  Total area: {puddle_area:.0f} pixels")
        print(f"  Result: {water_result}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["raw_detections"]["water"] = {"error": str(e)}
    
    # ========== DETECTOR 2: WASTE / CLUTTER ==========
    print("\n[2/4] WASTE & CLUTTER DETECTION")
    print("-" * 80)
    try:
        waste_detected, boxes, _, clutter_score = detect_waste(frame, water_mask=None)
        waste_with_mask = process_waste_frame(frame, water_mask=water_mask)
        
        results["raw_detections"]["waste_no_mask"] = {
            "detected": waste_detected,
            "objects": len(boxes),
            "clutter_score": round(clutter_score, 2),
            "issue": waste_detected
        }
        
        print(f"  Objects detected (no mask): {len(boxes)}")
        print(f"  Clutter score (no mask): {clutter_score:.2f}")
        print(f"  Waste detected (no mask): {waste_detected}")
        
        if water_mask is not None:
            waste_result_masked, _ = waste_with_mask
            results["raw_detections"]["waste_with_mask"] = {
                "detected": bool(waste_result_masked),
                "issue": waste_result_masked
            }
            print(f"\n  Objects detected (with water mask): {len(boxes) if waste_result_masked else 0}")
            print(f"  Waste detected (with water mask): {bool(waste_result_masked)}")
            
            # Check for conflict
            if waste_detected and not waste_result_masked:
                results["conflicts"].append({
                    "type": "FALSE_POSITIVE_WASTE",
                    "reason": "Waste detected but excluded due to water mask",
                    "clutter_score": clutter_score
                })
                print(f"\n  ⚠️  CONFLICT DETECTED: Waste likely due to water reflection/texture")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["raw_detections"]["waste"] = {"error": str(e)}
    
    # ========== DETECTOR 3: PERSON / UNAUTHORIZED ==========
    print("\n[3/4] PERSON DETECTION (Unauthorized Access)")
    print("-" * 80)
    try:
        person_detected = detect_person(frame)
        pose_detected = detect_person_mediapipe(frame)
        yolo_detected = detect_person_yolo(frame)
        
        results["raw_detections"]["person"] = {
            "detected": person_detected,
            "mediapipe_pose": pose_detected,
            "yolo_person": yolo_detected
        }
        
        print(f"  Person detected (combined): {person_detected}")
        print(f"    - MediaPipe pose: {pose_detected}")
        print(f"    - YOLO person: {yolo_detected}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["raw_detections"]["person"] = {"error": str(e)}
    
    # ========== DETECTOR 4: INFRASTRUCTURE (Lights & Fans) ==========
    print("\n[4/4] INFRASTRUCTURE ANALYSIS (Lights, Fans, Damage)")
    print("-" * 80)
    try:
        lights_detected = detect_artificial_light(frame)
        fan_detected = detect_fan_motion(frame)
        is_broken, severity, damage_details = detect_broken_infrastructure(frame)
        
        results["raw_detections"]["infrastructure"] = {
            "lights_detected": lights_detected,
            "fan_detected": fan_detected,
            "infrastructure_broken": is_broken,
            "damage_severity": severity,
            "damage_score": damage_details["total_damage_score"]
        }
        
        print(f"  Artificial lights: {lights_detected}")
        print(f"  Fan motion: {fan_detected}")
        print(f"  Broken infrastructure: {is_broken} (severity: {severity})")
        print(f"    - Damage score: {damage_details['total_damage_score']}")
        print(f"    - Crack score: {damage_details['crack_score']}")
        print(f"    - Dark areas: {damage_details['dark_areas_percentage']}%")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["raw_detections"]["infrastructure"] = {"error": str(e)}
    
    # ========== CONFLICT RESOLUTION ==========
    print("\n" + "="*80)
    print("CONFLICT RESOLUTION & VERIFICATION")
    print("="*80)
    
    # Simulate conflict resolution logic
    water_detected = results["raw_detections"].get("water", {}).get("detected", False)
    waste_detected = results["raw_detections"].get("waste_no_mask", {}).get("detected", False)
    person_detected = results["raw_detections"].get("person", {}).get("detected", False)
    clutter_score = results["raw_detections"].get("waste_no_mask", {}).get("clutter_score", 0)
    
    detection_list = []
    if water_detected:
        detection_list.append("water leak")
    if waste_detected:
        detection_list.append("waste/clutter")
    if person_detected:
        detection_list.append("person")
    
    if detection_list:
        print(f"\n⚠️  Multiple detections found: {', '.join(detection_list)}")
        
        if water_detected:
            print(f"   - Water leak: YES (PRIORITY)")
            results["verified_detections"]["water"] = results["raw_detections"]["water"]
        
        if person_detected:
            print(f"   - Person: YES (PRIORITY)")
            results["verified_detections"]["person"] = results["raw_detections"]["person"]
        
        if waste_detected:
            if water_detected and clutter_score < 15:
                print(f"   - Waste/Clutter: YES but DISCARDED (clutter_score={clutter_score:.2f}, likely water texture)")
            else:
                print(f"   - Waste/Clutter: YES (clutter_score={clutter_score:.2f})")
                results["verified_detections"]["waste"] = results["raw_detections"].get("waste_no_mask", {}).get("issue")
    
    else:
        print(f"\n✓ No major issues detected")
    
    # ========== SUMMARY ==========
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    print(f"\nRaw Detections:")
    for detector, data in results["raw_detections"].items():
        print(f"  {detector}: {data}")
    
    print(f"\nVerified Results:")
    if results["verified_detections"]:
        for detector, data in results["verified_detections"].items():
            print(f"  {detector}: {data}")
    else:
        print("  (No issues detected)")
    
    if results["conflicts"]:
        print(f"\nConflicts Resolved:")
        for conflict in results["conflicts"]:
            print(f"  - {conflict['type']}: {conflict['reason']}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Test ML engine with independent detectors and conflict resolution"
    )
    parser.add_argument("image_path", help="Path to test image")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    # Load image
    frame = cv2.imread(args.image_path)
    if frame is None:
        print(f"✗ Failed to load image: {args.image_path}")
        sys.exit(1)
    
    print(f"\n📷 Testing image: {args.image_path}")
    print(f"   Dimensions: {frame.shape}")
    
    # Run full pipeline test
    results = test_pipeline(frame, verbose=args.verbose)
    
    print("\n✓ Test completed successfully")


if __name__ == "__main__":
    main()
