import os
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np
import cv2
import joblib
from PIL import Image
from pathlib import Path

from sam_model import SAMModel
from mask_filter import get_final_mask
from feature_extractor import extract_features

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "xgb_final_model.pkl"
SAM_PATH = BASE_DIR / "sam_vit_b.pth"
THRESHOLD = 0.6

print("Loading models...")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load XGBoost model: {e}")

try:
    sam = SAMModel(SAM_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load SAM model: {e}")

print("Models loaded")

def engineer_features(features):
    epsilon = 1e-5
    features["texture_norm"] = features["texture_var"] / (features["area_ratio"] + epsilon)
    features["reflection_score"] = np.log(features["texture_var"] + 1) - np.log(features["laplacian_var"] + 1)
    features["edge_texture_ratio"] = features["laplacian_var"] / (features["texture_var"] + 1)
    return features

def predict(image: Image.Image):
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (512, 512))

    masks = sam.generate_masks(image)
    final_mask = get_final_mask(masks, image)

    if final_mask is None:
        return {
            "prediction": "no_detection",
            "confidence": 0.0
        }

    features = extract_features(image, final_mask)

    required_keys = ["texture_var", "laplacian_var", "shape_irregularity", "area_ratio"]
    for key in required_keys:
        if key not in features:
            raise ValueError(f"Missing feature: {key}")

    features = engineer_features(features)

    feature_vector = np.array([[
        features["texture_var"],
        features["laplacian_var"],
        features["shape_irregularity"],
        features["area_ratio"],
        features["texture_norm"],
        features["reflection_score"],
        features["edge_texture_ratio"]
    ]])

    prob = model.predict_proba(feature_vector)[0][1]
    label = "water_spill" if prob > THRESHOLD else "not_water_spill"

    return {
        "prediction": label,
        "confidence": float(round(prob, 4))
    }

if __name__ == "__main__":
    import gradio as gr

    def gradio_predict(image):
        try:
            result = predict(image)
            return result["prediction"], result["confidence"]
        except Exception as e:
            return f"Error: {str(e)}", 0.0

    iface = gr.Interface(
        fn=gradio_predict,
        inputs=gr.Image(type="pil"),
        outputs=["text", "number"],
        title="Water Spill Detection",
        description="Detects water spill vs reflection using SAM + XGBoost"
    )

    iface.launch()