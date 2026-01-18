from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from analyticsapp.models import AnalyticsSnapshotDaily
from analyticsapp.services.snapshots import snapshot_kpis


class SnapshotKpisCompletenessTests(TestCase):
    def test_snapshot_kpis_reports_incomplete_window(self):
        today = timezone.localdate()

        # 3-day window: [today-2, today-1, today]
        # Create snapshots for today and today-2 only (missing today-1).
        AnalyticsSnapshotDaily.objects.create(
            day=today, revenue=Decimal("10.00"), orders=1
        )
        AnalyticsSnapshotDaily.objects.create(
            day=today - timedelta(days=2), revenue=Decimal("5.00"), orders=1
        )

        out = snapshot_kpis(3)
        meta = out["meta"]

        self.assertFalse(meta["is_complete"])
        self.assertEqual(meta["missing_days"], 1)
        self.assertEqual(out["rev"]["revenue"], Decimal("15.00"))
        self.assertEqual(out["rev"]["orders"], 2)

    def test_snapshot_kpis_reports_complete_window(self):
        today = timezone.localdate()

        AnalyticsSnapshotDaily.objects.create(
            day=today, revenue=Decimal("10.00"), orders=1
        )
        AnalyticsSnapshotDaily.objects.create(
            day=today - timedelta(days=1), revenue=Decimal("7.00"), orders=1
        )
        AnalyticsSnapshotDaily.objects.create(
            day=today - timedelta(days=2), revenue=Decimal("5.00"), orders=1
        )

        out = snapshot_kpis(3)
        meta = out["meta"]

        self.assertTrue(meta["is_complete"])
        self.assertEqual(meta["missing_days"], 0)
        self.assertEqual(out["rev"]["revenue"], Decimal("22.00"))
        self.assertEqual(out["rev"]["orders"], 3)
