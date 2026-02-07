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

# Update this command based on how you start your app
CMD ["python", "ml_engine/api/inference_api.py"]
