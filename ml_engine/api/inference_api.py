from fastapi import FastAPI, UploadFile
import cv2
import numpy as np
from core.decision_engine import process_frame

app = FastAPI()

@app.post("/lights_off")
async def lights_off(file: UploadFile):
    data = await file.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

    result = process_frame(img)

    return result or {"status": "normal"}
