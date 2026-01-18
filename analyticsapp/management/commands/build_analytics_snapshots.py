from __future__ import annotations

from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from analyticsapp.models import AnalyticsProductDaily, AnalyticsSnapshotDaily
from analyticsapp.services.customers import customer_kpis
from analyticsapp.services.funnel import wishlist_funnel
from analyticsapp.services.revenue import revenue_kpis
from orders.models import OrderItem


class Command(BaseCommand):
    help = "Build daily analytics snapshots for the last N days (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=180,
            help="How many days back to backfill (default 180).",
        )

    def handle(self, *args, **options):
        days = int(options["days"])
        if days < 1:
            self.stdout.write(self.style.ERROR("--days must be >= 1"))
            return

        today = timezone.localdate()
        start_day = today - timedelta(days=days - 1)

        created = 0
        updated = 0
        product_rows_upserted = 0

        for i in range(days):
            day = start_day + timedelta(days=i)

            start_dt = timezone.make_aware(datetime.combine(day, time.min))
            end_dt = timezone.make_aware(datetime.combine(day, time.max))

            rev = revenue_kpis(start_dt, end_dt)
            cust = customer_kpis(start_dt, end_dt)
            funnel = wishlist_funnel(start_dt, end_dt)

            with transaction.atomic():
                # --- Daily KPI snapshot ---
                obj, was_created = (
                    AnalyticsSnapshotDaily.objects.select_for_update().get_or_create(
                        day=day
                    )
                )

                obj.revenue = rev["revenue"]
                obj.orders = rev["orders"]
                obj.aov = rev["aov"]

                obj.refunded_amount = rev.get("refund_amount", 0)
                obj.refunded_orders = rev.get("refunded_orders", 0)

                obj.unique_customers = cust.get("unique", 0)
                obj.repeat_customers = cust.get("repeat", 0)

                obj.wish_users = funnel.get("wish_users", 0)
                obj.purchased_users = funnel.get("purchased_users", 0)

                obj.save()

                if was_created:
                    created += 1
                else:
                    updated += 1

                # --- Product daily rollups (best sellers) ---
                # Some OrderItems may not have a Product FK (product is NULL). Exclude them.
                items = (
                    OrderItem.objects.filter(
                        order__status__in=("paid", "fulfilled"),
                        order__created_at__range=(start_dt, end_dt),
                        product__isnull=False,
                    )
                    .values("product_id")
                    .annotate(
                        units=Sum("qty"),
                        revenue=Sum("line_total"),
                    )
                )

                for row in items:
                    product_id = row.get("product_id")
                    if not product_id:
                        continue

                    AnalyticsProductDaily.objects.update_or_create(
                        day=day,
                        product_id=product_id,
                        defaults={
                            "units": int(row["units"] or 0),
                            "revenue": row["revenue"] or 0,
                        },
                    )
                    product_rows_upserted += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Snapshots built for {days} day(s). "
                f"created={created}, updated={updated}, product_rows_upserted={product_rows_upserted}"
            )
        )
