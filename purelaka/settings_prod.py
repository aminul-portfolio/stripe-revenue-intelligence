from __future__ import annotations

import os
import sys

from .settings import *  # noqa: F403


# Production-like toggles for Django's check --deploy gate.
DEBUG = False  # noqa: F405


# Minimal deploy security flags required by Django's security checks.
SESSION_COOKIE_SECURE = True  # noqa: F405
CSRF_COOKIE_SECURE = True  # noqa: F405

# HSTS: safe starter value. Increase after validation in real deployment.
SECURE_HSTS_SECONDS = 60  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Health/readiness must remain probe-friendly under prod-like runs.
# We keep HTTPS redirect enabled, but exempt healthz so it can return 200 on HTTP.
SECURE_REDIRECT_EXEMPT = [r"^monitoring/healthz/$"]  # noqa: F405


# HTTPS redirect policy:
# - Keep enabled for real prod-like runs
# - Disable automatically for test runs (Django test client uses http://testserver)
_RUNNING_TESTS = any(arg == "test" for arg in sys.argv)

if _RUNNING_TESTS:
    SECURE_SSL_REDIRECT = False  # noqa: F405
else:
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1") == "1"  # noqa: F405
