from __future__ import annotations

from .settings import *  # noqa: F403

# Production-like toggles for Django's check --deploy gate.
DEBUG = False  # noqa: F405

# Minimal deploy security flags required by Django's security checks.
SECURE_SSL_REDIRECT = True  # noqa: F405
SESSION_COOKIE_SECURE = True  # noqa: F405
CSRF_COOKIE_SECURE = True  # noqa: F405

# HSTS: set a safe starter value. Increase after validation in real deployment.
SECURE_HSTS_SECONDS = 60  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
