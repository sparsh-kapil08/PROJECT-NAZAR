from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional, Dict, Any
import cv2
import numpy as np
import traceback
from core.decision_engine import process_frame

from modules.water_leak.leak_pipeline import process_water_frame
from modules.waste_monitor.waste_pipeline import process_waste_frame
from detectors.person_detector import detect_person
from detectors.water_detector import detect_raw_puddles
from detectors.waste_detector import detect_waste as detect_waste_raw

app = FastAPI()


def convert_numpy_types(obj):
    """
    Recursively convert numpy types to Python native types for JSON serialization.
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def standardize_detection(detection_type: str, detection_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize any detection to the unified schema:
    {detection, category, severity, risks, confidence}
    """
    if detection_type == "water_leak":
        return {
            "detection": detection_data.get("issue", "Water Leak Detected"),
            "category": "Plumbing",
            "severity": detection_data.get("severity", "Medium").title(),
            "risks": "Water damage, mold growth, structural damage, slip hazard",
            "confidence": 85  # Water is very specific
        }
    
    elif detection_type == "waste":
        clutter_score = detection_data.get("details", {}).get("clutter_score", 0)
        confidence = min(int(clutter_score * 2.5), 95)
        return {
            "detection": detection_data.get("issue_type", "Waste/Clutter Detected"),
            "category": "Cleanliness",
            "severity": detection_data.get("severity", "Medium").title(),
            "risks": "Hazard to students, poor hygiene, pest attraction",
            "confidence": confidence
        }
    
    elif detection_type == "unauthorized_access":
        return {
            "detection": "Unauthorized Person Detected",
            "category": "Safety",
            "severity": "High",
            "risks": "Security breach, potential theft, safety concern",
            "confidence": 90
        }
    
    elif detection_type == "broken_infrastructure":
        damage_score = detection_data.get("details", {}).get("total_damage_score", 0)
        confidence = min(int(damage_score * 100), 95)
        return {
            "detection": "Broken Infrastructure Detected",
            "category": "Infrastructure",
            "severity": detection_data.get("severity", "Medium").title(),
            "risks": "Safety hazard, further deterioration, potential injury",
            "confidence": confidence
        }
    
    elif detection_type == "energy_waste":
        return {
            "detection": "Energy Waste Detected",
            "category": "Electrical",
            "severity": "Medium",
            "risks": "Increased electricity costs, environmental impact",
            "confidence": 70
        }
    
    else:
        return {
            "detection": "Unknown Detection",
            "category": "General",
            "severity": "Low",
            "risks": "Unknown risk",
            "confidence": 0
        }


def resolve_conflicts(detections: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent conflict resolution.
    
    IMPORTANT: Only return the MOST CONFIDENT detection.
    Don't report multiple issues from a single image.
    
    Special Rule: If infrastructure is broken, it takes priority over waste.
    (e.g., broken chair = broken infrastructure, NOT waste/clutter)
    
    Priority order (most specific first):
    1. Water leak (very specific, high confidence if detected)
    2. Broken infrastructure (structural damage - takes priority over waste)
    3. Person (exact match - specific)
    4. Waste/Clutter (but only if infrastructure is NOT broken)
    5. Energy waste (least specific, could be shadows/reflections)
    """
    
    verified = {}
    
    # Collect all detections with confidence scores
    candidates = []
    
    # Water leak - highest priority if present
    if detections.get("water_leak"):
        candidates.append({
            "type": "water_leak",
            "data": detections["water_leak"],
            "priority": 1,
            "confidence": 0.95  # Water is very specific
        })
    
    # Person - very specific
    if detections.get("unauthorized_access"):
        candidates.append({
            "type": "unauthorized_access",
            "data": detections["unauthorized_access"],
            "priority": 2,
            "confidence": 0.90
        })
    
    # Infrastructure damage - but only if VERY confident
    infrastructure_broken = False
    infra_data = detections.get("general_infrastructure")
    if infra_data and isinstance(infra_data, dict):
        if "broken_infrastructure" in infra_data:
            damage_data = infra_data["broken_infrastructure"]
            damage_score = damage_data.get("details", {}).get("total_damage_score", 0)
            
            # STRICT: Only report if HIGH confidence (>0.55)
            if damage_score > 0.55:
                infrastructure_broken = True
                candidates.append({
                    "type": "broken_infrastructure",
                    "data": {"broken_infrastructure": damage_data},
                    "priority": 3,
                    "confidence": min(damage_score, 1.0)
                })
        
        # Energy waste - lowest priority
        if "energy_waste" in infra_data:
            candidates.append({
                "type": "energy_waste",
                "data": {"energy_waste": infra_data["energy_waste"]},
                "priority": 5,
                "confidence": 0.65  # Low confidence due to false positives
            })
    
    # Waste/Clutter - moderate priority, but SKIP if infrastructure is broken
    # (A broken chair is infrastructure, not waste)
    if detections.get("waste") and not infrastructure_broken:
        waste_data = detections["waste"]
        clutter_score = waste_data.get("details", {}).get("clutter_score", 0)
        
        # STRICT: Only report if HIGH confidence (>25)
        if clutter_score > 25:
            candidates.append({
                "type": "waste",
                "data": detections["waste"],
                "priority": 4,
                "confidence": min(clutter_score / 40.0, 1.0)  # Normalize to 0-1
            })
    
    # If no candidates with confidence, return empty
    if not candidates:
        return {}
    
    # Sort by priority, then confidence
    candidates.sort(key=lambda x: (x["priority"], -x["confidence"]))
    
    # Return ONLY the top candidate - standardized
    best = candidates[0]
    detection_type = best["type"]
    detection_data = best["data"]
    
    # Unwrap nested structures for standardization
    if detection_type == "broken_infrastructure":
        detection_data = detection_data.get("broken_infrastructure", detection_data)
    elif detection_type == "energy_waste":
        detection_data = detection_data.get("energy_waste", detection_data)
    
    # Standardize to unified schema
    standardized = standardize_detection(detection_type, detection_data)
    
    return standardized

@app.post("/ML_analyze")
async def analyze_image(
    file: UploadFile = File(...),
    start_hour: Optional[int] = Form(None),
    end_hour: Optional[int] = Form(None),
    check_unauthorized: bool = Form(False),
    debug: bool = Form(False)
):
    """
    Analyze an image for multiple potential issues.
    Each detector runs independently and results are reconciled.
    
    Args:
        file: Image file to analyze
        debug: If True, return raw detection results from all detectors
    """
    try:
        contents = await file.read()
        frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        
        # Validate frame was decoded successfully
        if frame is None:
            return {"status": "ERROR", "message": "Could not decode image"}
        
        # Validate frame has valid dimensions
        if frame.shape[0] < 10 or frame.shape[1] < 10:
            return {"status": "ERROR", "message": "Image dimensions too small"}
        
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return {"status": "ERROR", "message": "Image must be a valid color image (BGR)"}

        # Dictionary to store all raw detections
        all_detections = {}
        
        # ====== DETECTOR 1: WATER LEAK ======
        water_result, water_mask = process_water_frame(frame)
        all_detections["water_leak"] = water_result
        
        # ====== DETECTOR 2: WASTE / CLUTTER ======
        # Now pass water mask to avoid false positives
        waste_result, _ = process_waste_frame(frame, water_mask)
        all_detections["waste"] = waste_result
        
        # ====== DETECTOR 3: PERSON / UNAUTHORIZED ACCESS ======
        # Always run person detection - don't make it optional
        person_detected = detect_person(frame)
        unauthorized_result = None
        
        if person_detected:
            # Check if we should flag as unauthorized
            if check_unauthorized:
                unauthorized_result = {
                    "status": "DETECTED",
                    "message": "Unauthorized person detected",
                    "severity": "High",
                    "context": "restricted_hours" if check_unauthorized else "restricted_area"
                }
            elif start_hour is not None and end_hour is not None:
                # Validate hours
                if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
                    unauthorized_result = {"status": "ERROR", "message": "Hours must be between 0 and 23"}
                else:
                    # Person found, hours provided - flag as unauthorized
                    unauthorized_result = {
                        "status": "DETECTED",
                        "message": f"Person detected outside allowed hours ({start_hour}-{end_hour})",
                        "severity": "High",
                        "context": "restricted_hours",
                        "start_hour": start_hour,
                        "end_hour": end_hour
                    }
            else:
                # Person detected but no time context - still report it
                unauthorized_result = {
                    "status": "DETECTED",
                    "message": "Person detected in camera",
                    "severity": "Medium",
                    "context": "general"
                }
        
        all_detections["unauthorized_access"] = unauthorized_result
        
        # ====== DETECTOR 4: GENERAL INFRASTRUCTURE (lights, fans, broken parts) ======
        infrastructure_result = process_frame(frame)
        all_detections["general_infrastructure"] = infrastructure_result
        
        # ====== CONFLICT RESOLUTION ======
        # Verify and reconcile multiple detections
        verified_results = resolve_conflicts(all_detections)
        
        # Convert numpy types to Python types for JSON serialization
        verified_results = convert_numpy_types(verified_results)
        all_detections = convert_numpy_types(all_detections)
        
        # If no issues found, return standardized "No Issue" response
        if not verified_results or all(v is None for v in verified_results.values()):
            return {
                "detection": "No Issue",
                "category": "General",
                "severity": "Low",
                "risks": "No known risks",
                "confidence": 0
            }
        
        # If debug mode, return both raw and verified
        if debug:
            # Check if infrastructure results exist
            infra_exists = all_detections.get("general_infrastructure") is not None
            energy_waste = False
            infrastructure_broken = False
            
            if infra_exists:
                infra_data = all_detections["general_infrastructure"]
                if isinstance(infra_data, dict):
                    energy_waste = "energy_waste" in infra_data
                    infrastructure_broken = "broken_infrastructure" in infra_data
            
            return {
                "status": "SUCCESS",
                "verified_detections": verified_results,
                "raw_detections": all_detections,
                "detection_summary": {
                    "water_detected": bool(all_detections.get("water_leak") is not None),
                    "waste_detected": bool(all_detections.get("waste") is not None),
                    "person_detected": bool(all_detections.get("unauthorized_access") is not None),
                    "energy_waste_detected": energy_waste,
                    "infrastructure_broken_detected": infrastructure_broken
                }
            }
        
        return verified_results

    except Exception as e:
        traceback.print_exc()
        error_response = {"status": "SERVER_ERROR", "error": str(e)}
        return convert_numpy_types(error_response)
