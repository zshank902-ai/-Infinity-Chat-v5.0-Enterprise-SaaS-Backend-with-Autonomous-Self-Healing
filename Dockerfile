FROM python:3.10-slim

# Create a non-root user for security (HuggingFace requirement in some cases)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /home/user/app

# Copy requirements and install
COPY --chown=user backend/requirements.txt* requirements.txt* ./
RUN pip install --no-cache-dir --user -r requirements.txt || echo "Requirements fail check"

# Copy the rest of the code
COPY --chown=user . .

# Move files from backend to root if they exist
RUN if [ -d "backend" ]; then cp -r backend/* .; fi

# Create data and memory directories with permissions
RUN mkdir -p data memory/vault memory/lessons

# Set PYTHONPATH to ensure imports work
ENV PYTHONPATH=/home/user/app

# HuggingFace Standard Port
EXPOSE 7860

# Start server with verbose logs
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "debug"]
