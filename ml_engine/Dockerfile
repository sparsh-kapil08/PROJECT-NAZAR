FROM python:3.10-slim

# Install system dependencies for OpenCV/MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Create the Hugging Face user (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Install Python requirements
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your local project files
COPY --chown=user . .

# Hugging Face MUST use port 7860
CMD ["uvicorn", "ml_engine.api.inference_api:app", "--host", "0.0.0.0", "--port", "7860"]