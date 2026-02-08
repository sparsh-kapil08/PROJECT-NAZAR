# ML Engine Testing Guide

This guide explains how to test the PROJECT NAZAR ML engine and validate detector accuracy.

## Overview

The ML engine consists of 4 independent detectors:

1. **Water Leak Detector** - Detects water puddles/spills
2. **Waste/Clutter Detector** - Detects trash, garbage, and general clutter
3. **Person Detector** - Detects people in the frame (always enabled)
4. **Infrastructure Analyzer** - Detects lights on and fan motion (energy waste)

Each detector runs independently, and results are verified using a conflict resolution system.

## Key Changes (v2)

### Person Detection - Now Always Enabled ✅

Previously, person detection only ran if you passed `check_unauthorized=True` as a parameter. **This is now fixed**:

- **Person detection ALWAYS runs** for every image
- Uses **dual detection methods** for higher reliability:
  - **MediaPipe**: Detects human body pose/landmarks
  - **YOLO**: Detects "person" class objects
  - Returns TRUE if **either method** detects a person
- Person is automatically flagged even without time constraints

### Improved Reliability

The new person detector is **more robust** because:
- YOLO catches people from different angles and positions
- MediaPipe is good at detecting full-body poses
- Using both methods = higher chance of detecting actual people
- No longer dependent on optional query parameters

## Running Tests

### Option 1: Test All Detectors Together

Test the complete ML pipeline with conflict resolution:

```bash
cd /workspaces/PROJECT-NAZAR/ml_engine
python test_ml_engine.py <path_to_image>
```

**Example:**
```bash
python test_ml_engine.py ~/test_water.jpg
```

This shows:
- Raw detection results from each detector
- How conflicts are resolved
- Final verified results

### Option 2: Test Individual Detectors

Test specific detectors in isolation:

```bash
python test_detectors.py <path_to_image> --detector [water|waste|person|light|fan|all]
```

**Examples:**

```bash
# Test only water detection
python test_detectors.py ~/test_water.jpg --detector water

# Test only waste detection
python test_detectors.py ~/test_waste.jpg --detector waste

# Test all detectors
python test_detectors.py ~/test_image.jpg --detector all
```

## Understanding Results

### Water Detector Output

```
[WATER DETECTOR TEST]
  ✓ Puddles detected: 3
  ✓ Total puddle area: 1500 pixels
  ✓ Water detected: YES
```

- **Puddles detected**: Number of distinct puddles found
- **Total puddle area**: Combined area of all puddles (pixels²)
- **Water detected**: YES if area > 250 pixels

### Waste Detector Output

```
[WASTE DETECTOR TEST]
  ✓ Trash objects detected: 2
  ✓ Clutter score: 15.45
  ✓ Waste detected: YES
```

- **Trash objects**: Number of trash items detected by YOLOv8
- **Clutter score**: Texture/edge metric (higher = more clutter)
- **Waste detected**: YES if objects found OR clutter_score > 18

### Person Detector Output

```
[PERSON DETECTOR TEST]
  ✓ Person detected: YES
    - MediaPipe pose: NO
    - YOLO person: YES
```

- **Person detected**: YES if either MediaPipe OR YOLO detects a person
- **MediaPipe pose**: Detects body landmarks/pose (good for clear full-body shots)
- **YOLO person**: Detects person class objects (good for varied angles/positions)

**Why dual detection?**
- YOLO alone might miss people in certain poses
- MediaPipe alone might miss people at angles where body landmarks aren't visible
- Combined = higher accuracy and fewer false negatives

### Infrastructure Analysis Output

```
[LIGHT DETECTOR TEST]
  ✓ Artificial lights detected: YES

[FAN MOTION DETECTOR TEST]
  ✓ Fan motion detected: NO
```

## Conflict Resolution

The API uses intelligent conflict resolution to avoid false positives:

### Scenario: Water + Waste Detection

When both water and waste are detected:

1. **Water gets priority** (more urgent)
2. **Waste is re-validated**:
   - If clutter_score < 15 → marked as false positive (likely water reflection)
   - If clutter_score >= 15 → kept as valid detection

```
⚠️  Multiple detections found:
   - Water leak: YES (PRIORITY)
   - Waste/Clutter: YES (clutter_score=12.5)

   ✓ Waste marked as FALSE POSITIVE (likely water texture)
   ✓ Final decision: KEEP WATER, DISCARD WASTE
```

## Adjusted Thresholds (v2)

Updated to reduce false positives:

| Detector | Old Threshold | New Threshold | Change |
|----------|---------------|---------------|--------|
| Waste Clutter | score > 12 | score > 18 | +50% |
| Waste Medium | score > 18 | score > 22 | +22% |
| Waste High | score > 28 | score > 32 | +14% |
| Waste Objects (Low) | >0 | >0 | - |
| Waste Objects (Medium) | >3 | >4 | +33% |
| Waste Objects (High) | >6 | >8 | +33% |

## Using Debug Mode in API

Get raw + verified results:

```bash
curl -X POST "http://localhost:7860/ML_analyze?debug=true" \
  -F "file=@test_image.jpg"
```

Response includes:
- **verified_detections**: Final results after conflict resolution
- **raw_detections**: Raw output from each detector
- **detection_summary**: Boolean flags for what each detector found

### Person Detection in API

Person detection now **always returns** whether a person was detected:

```json
{
  "unauthorized_access": {
    "status": "DETECTED",
    "message": "Person detected in camera",
    "severity": "Medium",
    "context": "general"
  }
}
```

**No need to pass `check_unauthorized=True`** anymore - person detection runs automatically!

Optional parameters still work:
- `check_unauthorized=true` → severity "High" + "restricted_hours" context
- `start_hour` + `end_hour` → checks if person is outside allowed time window

## Tips for Testing

1. **Test with real failure cases**: 
   - Water image: spill, puddle, wet floor
   - Waste image: trash, clutter, garbage
   - Mixed: wet floor with some trash

2. **Check frame dimensions**: Images must be at least 10x10 pixels

3. **Monitor performance**: Large images slow down detection

4. **Verify each detector independently** before testing together

## Files

- `test_detectors.py` - Test individual detectors
- `test_ml_engine.py` - Test full pipeline with conflict resolution
- `api/inference_api.py` - Main API with conflict resolution logic
- `detectors/*.py` - Individual detector modules

## Troubleshooting

### "Could not decode image"
- Ensure image is a valid JPG/PNG file
- Check file size and format

### "Image dimensions too small"
- Image must be at least 10x10 pixels
- Use higher resolution test images for better detection

### Detector returns unexpected results
- Run individual detector test to isolate the issue
- Check adjusted thresholds match your use case
- May need to retrain or adjust model confidence values

## Next Steps

1. Collect real-world test images
2. Run `test_ml_engine.py` on each
3. Verify results match expected output
4. Adjust thresholds if needed (in detector files)
5. Deploy with confidence!
