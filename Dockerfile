# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install python deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
RUN python -m pip install --no-cache-dir ruff pip-audit

# Copy app code
COPY . /app

# Add entrypoint (ensure executable)
RUN chmod +x /app/entrypoint.sh

# Create a non-root user and switch (basic container hygiene)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default command (compose can override)
CMD ["gunicorn", "-c", "gunicorn.conf.py", "purelaka.wsgi:application"]
