FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock ./
COPY agents/ ./agents/
COPY common/ ./common/
COPY hosts/ ./hosts/
COPY youtube-video-upload/ ./youtube-video-upload/

# Install Python dependencies using uv
RUN pip install uv \
    && uv pip install .

# Copy remaining files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/videogena2a-fad2fc91e862.json

# Default command
CMD ["uv", "run", "--app-dir", ".", "--reload", "hosts.cli"]
