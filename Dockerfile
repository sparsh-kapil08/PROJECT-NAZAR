FROM python:3.10-slim

# Install system dependencies and Node.js/npm
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    gnupg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r ml_engine/requirements.txt

# Install frontend dependencies
RUN npm install --unsafe-perm --legacy-peer-deps

# Expose backend and frontend ports
EXPOSE 8000
ARG FRONTEND_PORT=5000
EXPOSE ${FRONTEND_PORT}

# Add start script to run both services
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Run from ml_engine directory (the script will change directories as needed)
WORKDIR /app/ml_engine
CMD ["/start.sh"]
