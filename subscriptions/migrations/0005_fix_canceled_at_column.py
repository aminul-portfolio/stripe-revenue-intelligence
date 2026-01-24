from __future__ import annotations

from django.db import migrations


def _ensure_canceled_at_column(apps, schema_editor) -> None:
    """
    Repair migration: ensure DB has `canceled_at` column.

    Cases handled:
    - If `canceled_at` already exists: do nothing.
    - If only `cancelled_at` exists: rename column to `canceled_at`.
    - If neither exists: add `canceled_at` as nullable datetime.
    - If rename fails on a backend: add + copy values best-effort.
    """
    table = "subscriptions_subscription"
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        columns = {
            c.name for c in connection.introspection.get_table_description(cursor, table)
        }

    if "canceled_at" in columns:
        return

    if "cancelled_at" in columns:
        # Try rename first (works on SQLite >= 3.25, Postgres, etc.)
        try:
            schema_editor.execute(
                f'ALTER TABLE {table} RENAME COLUMN cancelled_at TO canceled_at;'
            )
            return
        except Exception:
            # Fallback: add column then copy values.
            pass

        # Add column if rename failed
        with connection.cursor() as cursor:
            cols_now = {
                c.name
                for c in connection.introspection.get_table_description(cursor, table)
            }
        if "canceled_at" not in cols_now:
            schema_editor.execute(
                f"ALTER TABLE {table} ADD COLUMN canceled_at datetime NULL;"
            )
        schema_editor.execute(
            f"UPDATE {table} SET canceled_at = cancelled_at "
            f"WHERE canceled_at IS NULL;"
        )
        return

    # Neither exists: add column
    schema_editor.execute(
        f"ALTER TABLE {table} ADD COLUMN canceled_at datetime NULL;"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0004_alter_subscription_status_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Fix the migration state: we want the canonical field name.
            state_operations=[
                migrations.RenameField(
                    model_name="subscription",
                    old_name="cancelled_at",
                    new_name="canceled_at",
                ),
            ],
            # Fix the physical DB schema to match runtime expectations.
            database_operations=[
                migrations.RunPython(_ensure_canceled_at_column, migrations.RunPython.noop),
            ],
        ),
    ]
