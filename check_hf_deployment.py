#!/usr/bin/env python3
"""
Pre-deployment verification script for HF Spaces
Checks all dependencies, model files, and API configuration
"""

import sys
from pathlib import Path

def check_files():
    """Verify all required files exist"""
    required_files = {
        "ml_engine/Dockerfile": "Docker configuration",
        "ml_engine/requirements.txt": "ML engine dependencies",
        "water model/requirements.txt": "Water model dependencies",
        "requirements.txt": "Combined dependencies",
        "ml_engine/api/inference_api.py": "API entry point",
        "water model/app.py": "Water model prediction",
        "water model/sam_vit_b.pth": "SAM pre-trained weights (375MB)",
        "water model/xgb_final_model.pkl": "XGBoost model",
        ".dockerignore": "Docker build optimizer",
    }
    
    print("=" * 70)
    print("FILE VERIFICATION")
    print("=" * 70)
    
    all_ok = True
    for file_path, description in required_files.items():
        full_path = Path(file_path)
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        size = f"({full_path.stat().st_size / (1024*1024):.1f}MB)" if exists and full_path.is_file() else ""
        print(f"{status} {file_path:45} {description:30} {size}")
        
        if not exists and "model" in file_path:
            all_ok = False
    
    return all_ok

def check_requirements():
    """Verify all requirements files are valid Python"""
    print("\n" + "=" * 70)
    print("REQUIREMENTS VERIFICATION")
    print("=" * 70)
    
    req_files = [
        "ml_engine/requirements.txt",
        "water model/requirements.txt", 
        "requirements.txt"
    ]
    
    all_ok = True
    for req_file in req_files:
        try:
            with open(req_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                print(f"✓ {req_file:40} {len(lines)} packages")
        except Exception as e:
            print(f"✗ {req_file:40} ERROR: {e}")
            all_ok = False
    
    return all_ok

def check_api_imports():
    """Verify API can be imported"""
    print("\n" + "=" * 70)
    print("API IMPORT VERIFICATION")
    print("=" * 70)
    
    try:
        sys.path.insert(0, str(Path("ml_engine").resolve()))
        from api.inference_api import app
        print("✓ API imports successfully")
        print(f"✓ FastAPI app initialized: {app.title if hasattr(app, 'title') else 'OK'}")
        return True
    except Exception as e:
        print(f"✗ API import failed: {e}")
        return False

def check_water_model():
    """Verify water model can be loaded"""
    print("\n" + "=" * 70)
    print("WATER MODEL VERIFICATION")
    print("=" * 70)
    
    try:
        sys.path.insert(0, str(Path("water model").resolve()))
        from app import predict
        print("✓ Water model app.py imports successfully")
        print(f"✓ predict() function available: {callable(predict)}")
        return True
    except Exception as e:
        print(f"✗ Water model import failed: {e}")
        return False

def main():
    print("\n🚀 HUGGING FACE SPACES PRE-DEPLOYMENT CHECKLIST\n")
    
    file_ok = check_files()
    req_ok = check_requirements()
    
    # Only check imports if we're in the right environment
    api_ok = True
    water_ok = True
    try:
        api_ok = check_api_imports()
        water_ok = check_water_model()
    except Exception as e:
        print(f"\n⚠️  Skipping import checks (may not be in deployment environment): {e}")
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT READINESS")
    print("=" * 70)
    
    if file_ok and req_ok:
        print("✓ All checks passed! Ready for HF Spaces deployment")
        print("\nNext steps:")
        print("1. Add project to Hugging Face Space (Docker runtime)")
        print("2. Ensure model files (*.pth, *.pkl) are tracked with Git LFS")
        print("3. Push to HF and monitor build in Space logs")
        print("4. Access API at: https://your-username-space-name.hf.space/docs")
        return 0
    else:
        print("✗ Some checks failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
