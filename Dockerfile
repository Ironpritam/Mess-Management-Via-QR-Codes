# Use official lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing pyc files and buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for OpenCV and PyZbar
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    zbar-tools \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source files
COPY . /app/

# Expose ports for Django (8000) and FastAPI (8001)
EXPOSE 8000 8001

# Default command: Run Django migrations and start server
CMD ["python", "main.py", "--web"]
