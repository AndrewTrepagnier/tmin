# TMIN Package Dockerfile
# Multi-stage build for development and production

# Base image with Python 3.11 (latest stable)
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Development stage
FROM base as development

# Copy package files
COPY pyproject.toml requirements.txt ./
COPY tmin/ ./tmin/
COPY tests/ ./tests/
COPY Makefile run_tests.py ./

# Install development dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e ".[dev]"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash tmin
RUN chown -R tmin:tmin /app
USER tmin

# Expose port for Jupyter if needed
EXPOSE 8888

# Default command for development
CMD ["bash"]

# Testing stage
FROM development as testing

# Run tests by default
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=tmin", "--cov-report=term-missing"]

# Production stage
FROM base as production

# Copy package files
COPY pyproject.toml requirements.txt ./
COPY tmin/ ./tmin/
COPY tests/ ./tests/
COPY Makefile run_tests.py ./

# Install only production dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash tmin
RUN chown -R tmin:tmin /app
USER tmin

# Default command for production
CMD ["tmin", "--help"]
