# Hugging Face Spaces Deployment Guide

## Overview
This project deploys a complete ML inference pipeline on Hugging Face Spaces with:
- **Water Detection**: SAM + XGBoost model for water spill/leak detection
- **Multi-detector Pipeline**: Waste, person, infrastructure analysis
- **FastAPI Backend**: RESTful API with standardized detection outputs

## Files for HF Spaces Deployment

### Required Files
- `Dockerfile` - Container configuration (uses ml_engine/Dockerfile by default)
- `requirements.txt` - All Python dependencies with pinned versions
- `ml_engine/requirements.txt` - ML engine specific dependencies
- `water model/requirements.txt` - Water model dependencies
- `.dockerignore` - Reduce image size by excluding unnecessary files

### Project Structure
```
PROJECT-NAZAR-main/
├── ml_engine/
│   ├── api/
│   │   └── inference_api.py          # FastAPI entry point
│   ├── core/
│   ├── detectors/
│   ├── modules/
│   ├── utils/
│   ├── requirements.txt
│   └── Dockerfile                     # Container config
├── water model/
│   ├── app.py                         # Water detection model
│   ├── sam_model.py                   # SAM wrapper
│   ├── feature_extractor.py
│   ├── mask_filter.py
│   ├── sam_vit_b.pth                  # Pre-trained SAM weights
│   ├── xgb_final_model.pkl            # Pre-trained XGBoost model
│   └── requirements.txt
└── requirements.txt                   # Combined dependencies
```

## Deployment Steps

### Step 1: Create Hugging Face Space
1. Go to huggingface.co
2. Create new Space → Select "Docker" runtime
3. Link your GitHub repository or upload directly

### Step 2: Configure Space Settings
- **Runtime**: Docker
- **Port**: 7860 (automatic for HF Spaces)
- **Environment Variables**: (optional)
  - `OMP_NUM_THREADS=1` (already set in Dockerfile)
  - `PYTHONUNBUFFERED=1` (already set in Dockerfile)

### Step 3: Add Model Files
Ensure these large files are committed or uploaded to HF:
```
water model/sam_vit_b.pth (375MB)
water model/xgb_final_model.pkl (500KB)
ml_engine/yolov8n.pt (6MB)
```

You can use Git LFS:
```bash
git lfs install
git lfs track "*.pth"
git lfs track "*.pt"
git add .gitattributes
git commit -m "Track large model files with LFS"
git push
```

### Step 4: Monitor Deployment
- HF Spaces will build the Docker image automatically
- Check logs in the Space's "Logs" tab
- Service runs on `https://your-username-space-name.hf.space`

## API Endpoints

### Main Analysis Endpoint
```
POST /ML_analyze
```

**Request:**
```python
import requests
from PIL import Image

image = Image.open("test_image.jpg")
response = requests.post(
    "https://your-space.hf.space/ML_analyze",
    files={"file": image},
    data={
        "debug": False,
        "check_unauthorized": False,
        "start_hour": None,
        "end_hour": None
    }
)
```

**Response (Example - Water Detected):**
```json
{
  "detection": "Water Leak Detected",
  "category": "Plumbing",
  "severity": "High",
  "risks": "Water damage, mold growth, structural damage, slip hazard",
  "confidence": 85
}
```

**Debug Mode Response:**
```json
{
  "status": "SUCCESS",
  "verified_detections": { ... },
  "raw_detections": { ... },
  "water_model": {
    "water_model_status": "detected",
    "prediction": "water_spill",
    "confidence_score": 0.92,
    "fallback_used": false
  },
  "detection_summary": { ... }
}
```

## Local Testing Before Deployment

### Build and Run Locally
```bash
mkdir -p model_cache
cd PROJECT-NAZAR-main
docker build -f ml_engine/Dockerfile -t nazar-ml:latest .
docker run -p 7860:7860 --name nazar-ml nazar-ml:latest
```

### Or with Docker Compose
```bash
docker-compose up --build
```

Access API at: `http://localhost:7860/docs` (Swagger UI)

## Performance Notes

### Resource Recommendations for HF Spaces
- **CPU**: Standard (sufficient for inference)
- **Memory**: 16GB+ recommended (SAM requires ~10GB)
- **Storage**: 100GB recommended (for model weights)

### Inference Speed
- Water model with SAM: ~5-15 seconds per image (CPU)
- Full pipeline: ~20-30 seconds (all detectors)
- Bottleneck: SAM mask generation on CPU

### Optimization Options
1. **Reduce SAM points_per_side** in [water model/sam_model.py](water%20model/sam_model.py):
   ```python
   points_per_side=12  # Default 24, reduces inference time
   ```

2. **Use GPU** (if available on HF Spaces):
   - Set `device = "cuda"` in sam_model.py
   - Reduces inference to ~1-3 seconds

3. **Enable Caching** in FastAPI for repeated images

## Troubleshooting

### Build Fails: "No space left on device"
- Reduce Docker image by removing test files
- Clear unused build cache: `docker system prune`

### Model Loading Errors
- Ensure `.pth` and `.pkl` files are tracked with Git LFS
- Check file paths in [water model/app.py](water%20model/app.py) are absolute

### Slow Inference
- Check `OMP_NUM_THREADS=1` is set (prevents CPU overload)
- SAM CPU inference is inherently slow; GPU recommended for production

### Port Issues
- HF Spaces always exposes port 7860
- Do not change port in Dockerfile CMD

## Monitoring & Logging

View logs in HF Space's Logs tab:
```
INFO: Uvicorn running on http://0.0.0.0:7860
INFO: Application startup complete
```

Each request logs:
- Status code
- Response time
- Detection results (with debug=True)

## Next Steps

1. **Add Persistent Storage**: Use HF Spaces Persistent Storage for cached results
2. **Add Authentication**: Protect endpoints with API keys
3. **Set Up Webhooks**: Auto-rebuild on model updates
4. **Monitor Usage**: Track requests and inference time
5. **Scale Resources**: Upgrade to GPU if inference too slow

## Support

For issues specific to:
- **Hugging Face Spaces**: Check HF documentation
- **FastAPI**: See inference_api.py structure
- **Water Model**: See water model/README or app.py comments
