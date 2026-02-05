from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
from core.decision_engine import process_frame
from fastapi.middleware.cors import CORSMiddleware
import traceback

from modules.water_leak.leak_pipeline import process_water_frame
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def read_image(file):
    data = np.frombuffer(file, np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


@app.post("/ML_analyze")
async def detect_water(file: UploadFile = File(...)):

    try:
        file_data = await file.read()
        frame = read_image(file_data)

        if frame is None:
            return {"status": "ERROR", "message": "Could not decode image"}

        result, _ = process_water_frame(frame)

        if result:
            return {
                "status": "ISSUE_CONFIRMED",
                "data": result
            }
        else:
        
            async def lights_off(data):
                img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    return {"status": "ERROR", "message": "Could not decode image in lights_off"}
                result = process_frame(img)

                return result or {"status": "normal"}
            return await lights_off(file_data)
    except Exception as e:
        traceback.print_exc()
        return {"status": "SERVER_ERROR", "error": str(e)}
