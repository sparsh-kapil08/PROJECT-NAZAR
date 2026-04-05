FROM python:3.10-slim

# Install system dependencies for OpenCV/MediaPipe/PyTorch/SAM
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create the Hugging Face user (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    OMP_NUM_THREADS=1 \
    PYTHONUNBUFFERED=1
WORKDIR $HOME/app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy ml_engine requirements first (base dependencies)
COPY --chown=user ml_engine/requirements.txt ./ml_engine_requirements.txt
RUN pip install --no-cache-dir -r ml_engine_requirements.txt

# Copy water model requirements
COPY --chown=user water_model/requirements.txt ./water_model_requirements.txt
RUN pip install --no-cache-dir -r water_model_requirements.txt

# Copy project structure
COPY --chown=user ml_engine ./ml_engine
COPY --chown=user water_model ./water_model
COPY --chown=user . .

# Expose port for Hugging Face Spaces (7860 is standard for HF)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/docs', timeout=5)" || exit 1

# Hugging Face Spaces entry point
CMD ["uvicorn", "ml_engine.api.inference_api:app", "--host", "0.0.0.0", "--port", "7860"]