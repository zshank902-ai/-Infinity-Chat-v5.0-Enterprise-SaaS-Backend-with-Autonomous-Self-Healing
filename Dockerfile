FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Try to copy requirements from either root or backend/
COPY requirements.txt* backend/requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r backend/requirements.txt || echo "Requirements already handled"

# Copy everything
COPY . .

# Move files from backend to root if they exist (to avoid path issues)
RUN if [ -d "backend" ]; then cp -r backend/* .; fi

# Create data and memory directories
RUN mkdir -p data memory/vault memory/lessons

# Set PYTHONPATH to root
ENV PYTHONPATH=/app

# Expose HuggingFace standard port
EXPOSE 7860

# Start server with 0.0.0.0 to ensure external access
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "debug"]
