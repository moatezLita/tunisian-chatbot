FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for data and models
RUN mkdir -p data model resources

# Set up entry point
ENTRYPOINT ["python", "main.py"]

# Default command (can be overridden)
CMD ["--mode", "chat"]