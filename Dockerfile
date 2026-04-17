# Dockerfile
# KarunaAI API - HuggingFace Spaces Docker deployment
# HF Spaces membutuhkan Dockerfile di root repository

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install dependencies terlebih dahulu (layer caching)
COPY requirements-spaces.txt .
RUN pip install --no-cache-dir -r requirements-spaces.txt

# Copy seluruh application code
COPY . .

# Buat directory models jika belum ada
RUN mkdir -p models/emotion_engine/final models/crisis_detector/final

# HuggingFace Spaces menjalankan container sebagai user dengan uid 1000
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

# HuggingFace Spaces mengekspos port 7860
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Jalankan FastAPI via uvicorn pada port 7860 (standar HF Spaces)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
