from __future__ import annotations

from django.conf import settings
from django.test.runner import DiscoverRunner

import psycopg


class PostgresTerminatingDiscoverRunner(DiscoverRunner):
    """
    Fixes Postgres test teardown on Docker/WSL where lingering sessions can block
    DROP DATABASE for the Django test database.
    """

    def teardown_databases(self, old_config, **kwargs):
        for db in settings.DATABASES.values():
            engine = (db.get("ENGINE") or "").lower()
            test_name = (db.get("TEST") or {}).get("NAME")
            if "postgresql" in engine and test_name:
                self._terminate_test_db_sessions(db, test_name)
        return super().teardown_databases(old_config, **kwargs)

    def _terminate_test_db_sessions(self, db: dict, test_db_name: str) -> None:
        host = db.get("HOST") or "127.0.0.1"
        port = db.get("PORT") or "5432"
        user = db.get("USER") or ""
        password = db.get("PASSWORD") or ""

        try:
            with psycopg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname="postgres",
                autocommit=True,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT pg_terminate_backend(pid) "
                        "FROM pg_stat_activity "
                        "WHERE datname = %s AND pid <> pg_backend_pid();",
                        (test_db_name,),
                    )
        except Exception:
            # Do not mask real test failures; Django will still attempt teardown.
            return
