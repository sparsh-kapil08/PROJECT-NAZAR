FROM python:3.11-slim

# Install system dependencies (minimal for Hugging Face)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ml_engine/requirements.txt

# Expose API port
EXPOSE 7860

# Set working directory for API
WORKDIR /app/ml_engine

# Run only the FastAPI backend (Hugging Face will handle the interface)
CMD ["uvicorn", "api.inference_api:app", "--host", "0.0.0.0", "--port", "7860"]
