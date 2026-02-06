from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
import cv2
import numpy as np
import traceback
from core.decision_engine import process_frame

from modules.water_leak.leak_pipeline import process_water_frame
from modules.waste_monitor.waste_pipeline import process_waste_frame
app = FastAPI()

@app.post("/ML_analyze")
async def analyze_image(
    file: UploadFile = File(...),
    start_hour: Optional[int] = Form(None),
    end_hour: Optional[int] = Form(None)
):
    """
    Single endpoint to analyze an image for multiple potential issues.
    It runs a pipeline of detectors: water, waste, and then general infrastructure.
    """
    try:
        contents = await file.read()
        frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return {"status": "ERROR", "message": "Could not decode image"}

        results = {}

        # Pipeline Step 1: Water Leak Detection
        water_result, _ = process_water_frame(frame)
        if water_result:
            results["water_leak"] = water_result

        # Pipeline Step 2: Waste Detection
        waste_result, _ = process_waste_frame(frame)
        if waste_result:
            results["waste"] = waste_result

        # Pipeline Step 3: Unauthorized Access Detection (if configured)
        if start_hour is not None and end_hour is not None:
            if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
                results["unauthorized_access"] = {"status": "ERROR", "message": "Hours must be between 0 and 23"}
            else:
                # Placeholder for unauthorized detection logic
                # result = detector.process_frame(frame, start_hour, end_hour)
                # if result: results["unauthorized_access"] = result
                # results["unauthorized_access"] = {"status": "NOT_IMPLEMENTED", "message": "Unauthorized detector module missing"}
                pass

        # Pipeline Step 4: General Infrastructure Analysis
        general_result = process_frame(frame)
        if general_result:
            results["general_infrastructure"] = general_result

        # If no specific issues are found by any model, return a normal status
        if not results:
            return {"status": "NORMAL"}

        return results

    except Exception as e:
        traceback.print_exc()
        return {"status": "SERVER_ERROR", "error": str(e)}
