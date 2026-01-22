from __future__ import annotations

from typing import Any

from django.test.runner import DiscoverRunner


class SafePostgresTeardownRunner(DiscoverRunner):
    """
    Postgres-only guardrail for local Docker/WSL: terminate lingering sessions
    to the *test database* before Django tries to drop it.

    No-ops safely when:
      - psycopg is not installed
      - the active DB engine is not Postgres
    """

    def teardown_databases(self, old_config: Any, **kwargs: Any) -> None:
        self._terminate_postgres_test_db_sessions_safely(old_config)
        return super().teardown_databases(old_config, **kwargs)

    def _terminate_postgres_test_db_sessions_safely(self, old_config: Any) -> None:
        # Django returns a LIST of tuples from setup_databases():
        #   [(connection, old_name, destroy), ...]
        # Some legacy paths may pass dict-like configs; we support both.
        items: list[tuple[Any, Any, Any]] = []

        if isinstance(old_config, list):
            items = old_config
        elif isinstance(old_config, dict):
            # best-effort fallback
            items = [(None, None, None)]  # will no-op
        else:
            return  # unknown shape; do nothing

        # psycopg is optional (CI may not have it)
        try:
            import psycopg  # type: ignore
        except Exception:
            return

        for entry in items:
            if not isinstance(entry, (tuple, list)) or len(entry) < 1:
                continue

            connection = entry[0]
            if connection is None:
                continue

            engine = str(connection.settings_dict.get("ENGINE", ""))
            if "postgresql" not in engine:
                continue  # only for Postgres

            # Determine test DB name robustly
            try:
                test_db_name = connection.creation._get_test_db_name()  # type: ignore[attr-defined]
            except Exception:
                test_db_name = connection.settings_dict.get("NAME")

            if not test_db_name:
                continue

            s = connection.settings_dict
            host = s.get("HOST") or "127.0.0.1"
            port = s.get("PORT") or "5432"
            user = s.get("USER") or ""
            password = s.get("PASSWORD") or ""

            # Connect to maintenance DB and terminate sessions on the test DB
            try:
                admin = psycopg.connect(
                    dbname="postgres",
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    connect_timeout=3,
                )
                admin.autocommit = True
                with admin.cursor() as cur:
                    cur.execute(
                        """
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = %s
                          AND pid <> pg_backend_pid();
                        """,
                        (test_db_name,),
                    )
                admin.close()
            except Exception:
                # Never fail the test run because the cleanup helper failed.
                # Django will still attempt normal teardown.
                pass


# Backwards-compatible alias (matches TEST_RUNNER setting)
PostgresTerminatingDiscoverRunner = SafePostgresTeardownRunner
