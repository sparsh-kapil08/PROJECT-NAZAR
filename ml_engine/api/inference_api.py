from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import traceback
from core.decision_engine import process_frame

from modules.water_leak.leak_pipeline import process_water_frame
from modules.waste_monitor.waste_pipeline import process_waste_frame
app = FastAPI()

@app.post("/ML_analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Single endpoint to analyze an image for multiple potential issues.
    It runs a pipeline of detectors: water, waste, and then general infrastructure.
    """
    try:
        contents = await file.read()
        frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return {"status": "ERROR", "message": "Could not decode image"}

        # Pipeline Step 1: Water Leak Detection
        water_result, _ = process_water_frame(frame)
        if water_result:
            return water_result

        # Pipeline Step 2: Waste Detection
        waste_result, _ = process_waste_frame(frame)
        if waste_result:
            return waste_result

        # Pipeline Step 3: General Infrastructure Analysis (fallback)
        general_result = process_frame(frame)
        if general_result:
            return general_result

        # If no specific issues are found by any model, return a normal status
        return {"status": "NORMAL"}

    except Exception as e:
        traceback.print_exc()
        return {"status": "SERVER_ERROR", "error": str(e)}
