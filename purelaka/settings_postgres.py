from __future__ import annotations

import os

from .settings import *  # noqa: F403


DB_NAME = os.getenv("DB_NAME", "purelaka")
DB_USER = os.getenv("DB_USER", "purelaka")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 0,  # keep test connections short-lived
        "TEST": {
            "NAME": f"test_{DB_NAME}_{DB_USER}",
            "TEMPLATE": "template0",
        },
    }
}
TEST_RUNNER = "purelaka.test_runner.PostgresTerminatingDiscoverRunner"
