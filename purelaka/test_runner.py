from __future__ import annotations

from django.test.runner import DiscoverRunner


class PostgresTerminatingDiscoverRunner(DiscoverRunner):
    """
    Postgres teardown reliability helper.

    In some Docker/WSL environments, Django's Postgres test DB drop can fail with:
      OperationalError: database "test_..." is being accessed by other users

    This runner attempts to terminate lingering sessions before teardown.
    It is safe to import and run even when psycopg is not installed (e.g., CI on SQLite),
    in which case it becomes a no-op and falls back to default behavior.
    """

    def teardown_databases(self, old_config, **kwargs):
        self._terminate_postgres_test_db_sessions_safely(old_config)
        return super().teardown_databases(old_config, **kwargs)

    def _terminate_postgres_test_db_sessions_safely(self, old_config):
        try:
            import psycopg  # type: ignore
        except Exception:
            # CI or environments without psycopg: no-op.
            return

        # old_config shape is not strictly stable across Django versions; handle defensively.
        for alias, conn_info in old_config.items():
            try:
                conn = conn_info.get("connection")
                test_db_name = conn_info.get("name")
                if conn is None or not test_db_name:
                    continue

                engine = conn.settings_dict.get("ENGINE", "")
                if "postgresql" not in engine:
                    continue

                user = conn.settings_dict.get("USER", "")
                password = conn.settings_dict.get("PASSWORD", "")
                host = conn.settings_dict.get("HOST", "")
                port = conn.settings_dict.get("PORT", "")

                # Connect to the maintenance DB and terminate sessions for the test DB.
                conninfo = f"dbname=postgres user={user} host={host} port={port}"
                if password:
                    conninfo += f" password={password}"

                with psycopg.connect(conninfo, autocommit=True) as admin_conn:
                    with admin_conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT pg_terminate_backend(pid)
                            FROM pg_stat_activity
                            WHERE datname = %s
                              AND pid <> pg_backend_pid();
                            """,
                            (test_db_name,),
                        )
            except Exception:
                # Never fail the test run because of cleanup attempts.
                continue
