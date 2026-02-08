FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r ml_engine/requirements.txt

# Expose port if needed (adjust as needed)
EXPOSE 8000

# Use uvicorn to run the FastAPI app
CMD ["uvicorn", "ml_engine.api.inference_api:app", "--host", "0.0.0.0", "--port", "8000"]
