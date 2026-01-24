from __future__ import annotations

from django.db import migrations, models


SUBSCRIPTION_STATUS_VALUES = (
    "incomplete",
    "incomplete_expired",
    "trialing",
    "active",
    "past_due",
    "canceled",
    "unpaid",
    "paused",
)


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0005_fix_canceled_at_column"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.CheckConstraint(
                name="subscription_status_valid",
                check=models.Q(status__in=SUBSCRIPTION_STATUS_VALUES),
            ),
        ),
    ]
