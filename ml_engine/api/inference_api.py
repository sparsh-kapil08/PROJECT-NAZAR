from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
from core.decision_engine import process_frame

from modules.water_leak.leak_pipeline import process_water_frame
from modules.waste_monitor.waste_pipeline import process_waste_frame
app = FastAPI()



def read_image(file):
    data = np.frombuffer(file, np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


@app.post("/water-detect")
async def detect_water(file: UploadFile = File(...)):

    frame = read_image(await file.read())

    result, _ = process_water_frame(frame)

    if result:
        return {
            "status": "ISSUE_CONFIRMED",
            "data": result
        }

    return {"status": "NO_ISSUE"}

@app.post("/lights_off")
async def lights_off(file: UploadFile):
    data = await file.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

    result = process_frame(img)

    return result or {"status": "normal"}

@app.post("/waste-detect")
async def waste_detect(file: UploadFile = File(...)):

    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    result, _ = process_waste_frame(frame)

    if result is None:
        return {"status": "clean"}

    return {
        "issue": result["issue"],
        "severity": result["severity"],
        "clutter_score": float(result["clutter_score"]),
        "objects": int(result["objects"])
    }

