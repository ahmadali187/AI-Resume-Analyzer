# Dockerfile for AI Resume Analyzer & ATS Optimizer
FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable stdout buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose port
EXPOSE 5000

# Start Gunicorn server
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:create_app()"]
