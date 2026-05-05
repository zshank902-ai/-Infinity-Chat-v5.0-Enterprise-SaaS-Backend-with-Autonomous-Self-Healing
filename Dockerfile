FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for HuggingFace
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy files with correct ownership
COPY --chown=user . $HOME/app

# Install requirements as user
RUN pip install --no-cache-dir --user -r requirements.txt

# Create necessary directories
RUN mkdir -p data memory/vault memory/lessons projects

# HuggingFace Standard Port
EXPOSE 7860

# Start server
CMD ["python", "main.py"]
