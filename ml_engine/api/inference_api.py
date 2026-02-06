from fastapi import FastAPI, UploadFile, File, Form 
import cv2
import numpy as np
from core.decision_engine import process_frame


from modules.water_leak.leak_pipeline import process_water_frame, reset_state
from modules.waste_monitor.waste_pipeline import process_waste_frame
from modules.unauthorised_monitor.detector import detector
from detectors.broken_infra_detector import BrokenInfrastructureDetector


app = FastAPI()



def read_image(file):
    data = np.frombuffer(file, np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

broken_infra_detector = BrokenInfrastructureDetector(
    model_path="yolov8n.pt"
)


def read_image(file: UploadFile):
    contents = file.file.read()
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    return img


@app.post("/detect/broken-infrastructure")
async def detect_broken_infrastructure(
    file: UploadFile = File(...)
):
    frame = read_image(file)

    if frame is None:
        return {
            "success": False,
            "message":"Invalid image"
        }

    detections = broken_infra_detector.detect(frame)

    return {
        "success": True,
        "issue": "broken_infrastructure",
        "detected_count": len(detections),
        "detections": detections
    }


@app.post("/water-detect")
async def detect_water(file: UploadFile = File(...)):

    reset_state()   # <-- this is the missing brain wipe

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

@app.post("/detect/unauthorized")
async def detect_unauthorized(
    image: UploadFile = File(...),
    start_hour: int = Form(...),
    end_hour: int = Form(...)
    ):
    if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
        return {"error": "Hours must be between 0 and 23"}

    contents = await image.read()
    np_img = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Invalid image"}

    result = detector.process_frame(frame, start_hour, end_hour)
    return result
