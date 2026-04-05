# Hugging Face Spaces Deployment - Quick Start

✅ **All systems ready for deployment**

## What We've Prepared

### 1. **Optimized Dependencies**
- ✓ `ml_engine/requirements.txt` - 16 pinned packages
- ✓ `water model/requirements.txt` - 10 pinned packages  
- ✓ `requirements.txt` - 18 unified packages (master copy)
- ✓ All dependencies compatible with Python 3.10 slim base image

### 2. **Production-Ready Dockerfile**
- ✓ Multi-stage Build System
- ✓ HF Spaces optimized (port 7860, non-root user)
- ✓ Build dependencies for PyTorch/SAM compilation
- ✓ Health checks included
- ✓ Size-optimized with `.dockerignore`

### 3. **Water Model Integration**
- ✓ SAM + XGBoost model wired into API
- ✓ Model files included (357.7MB + 0.4MB)
- ✓ Verified runtime loading ✓
- ✓ Fallback path for resilience

### 4. **Documentation**
- ✓ `HF_DEPLOYMENT.md` - Full deployment guide
- ✓ `docker-compose.yaml` - Local testing setup
- ✓ `.dockerignore` - Build optimization
- ✓ `check_hf_deployment.py` - Pre-flight verification

## Quick Deployment (3 Steps)

### Step 1: Create HF Space
```bash
# Go to huggingface.co → New Space
# Config:
# - Name: project-nazar-ml (or your choice)
# - License: MIT
# - Runtime: Docker
# - Private: False (or True if you prefer)
```

### Step 2: Push to HF
```bash
# Add HF remote to your repo
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/project-nazar-ml

# Ensure large files use Git LFS
git lfs install
git lfs track "*.pth" "*.pt" "*.pkl"

# Push to HF Spaces
git push hf main
```

### Step 3: Monitor & Access
```
# HF Spaces will:
1. Build Docker image automatically
2. Initialize container (2-5 minutes)
3. Start FastAPI server on port 7860

# Once running:
API Docs: https://your-username-project-nazar-ml.hf.space/docs
API Root: https://your-username-project-nazar-ml.hf.space
```

## API Usage Example

### Python
```python
import requests
from PIL import Image

# Load test image
image = Image.open("test.jpg")

# Call water detection endpoint
response = requests.post(
    "https://your-space.hf.space/ML_analyze",
    files={"file": image},
    data={
        "debug": True,
        "check_unauthorized": False
    }
)

print(response.json())
```

### cURL
```bash
curl -X POST "https://your-space.hf.space/ML_analyze" \
  -F "file=@test.jpg" \
  -F "debug=true"
```

### Response
```json
{
  "status": "SUCCESS",
  "verified_detections": {
    "detection": "Water Leak Detected",
    "category": "Plumbing",
    "severity": "High",
    "risks": "Water damage, mold growth...",
    "confidence": 92
  },
  "water_model": {
    "water_model_status": "detected",
    "prediction": "water_spill",
    "confidence_score": 0.92,
    "fallback_used": false
  }
}
```

## File Sizes
```
Total Package Size: ~1.2GB (Docker image)
- Python 3.10 base: ~900MB
- PyTorch + dependencies: ~600MB (cached)
- SAM weights: 357.7MB (included)
- Other models & packages: ~100MB
```

## Key Deployment Checks ✓

```
✓ Dockerfile syntax valid
✓ All requirements pinned to versions
✓ API imports successfully
✓ Water model loads and predicts
✓ Model files present (357.7MB + 0.4MB)
✓ Port configuration correct (7860)
✓ Non-root user setup (UID 1000)
✓ Health checks configured
```

## Troubleshooting

### Container Won't Start
→ Check logs in HF Space → Logs tab
→ Verify model files are in repo
→ Check Git LFS tracking

### Slow Inference (>30s)
→ CPU inference of SAM is slow by design
→ Consider GPU upgrade if available
→ Or reduce `points_per_side` in water_model/sam_model.py

### Out of Memory
→ Increase Space resources in settings
→ Or optimize batch processing
→ SAM needs ~10GB RAM on CPU

### Build Timeout
→ Try pushing smaller chunks
→ Use Git LFS for models
→ Check internet connection

## Next Steps After Deployment

1. **Add front-end UI**
   - Use Gradio wrapper around FastAPI
   - Deploy separate Gradio Space

2. **Enable persistent storage**
   - Store analysis logs
   - Cache inference results

3. **Set up monitoring**
   - Track request count
   - Monitor inference times
   - Alert on errors

4. **Optimize performance**
   - GPU upgrade for faster inference
   - Batch processing
   - Model quantization

## Support Links

- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- FastAPI Docs: https://fastapi.tiangolo.com/
- Docker Docs: https://docs.docker.com/
- SAM Paper: https://arxiv.org/abs/2304.02643

---

**Status**: ✅ Ready for deployment  
**Last Updated**: 2026-04-05  
**Deployment Guide**: See HF_DEPLOYMENT.md for detailed instructions
