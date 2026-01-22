# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for common Python wheels and runtime needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install python deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
RUN python -m pip install --no-cache-dir ruff pip-audit

# Copy app code
COPY . /app

# Default port for local container runs (compose can override)
EXPOSE 8000

# Default command (compose can override)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
