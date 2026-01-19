from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.services.roles import set_role

User = get_user_model()


class AnalyticsExportsCsvTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.customer = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="pass12345",
        )

        self.ops = User.objects.create_user(
            username="ops1",
            email="ops1@example.com",
            password="pass12345",
        )
        set_role(self.ops, "ops")

        self.admin = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="pass12345",
            is_staff=True,
            is_superuser=True,
        )
        # Optional: if your decorator relies on get_role() for admin, set it explicitly too.
        set_role(self.admin, "admin")

        self.urls = [
            reverse("analytics-export-kpi-summary") + "?days=30",
            reverse("analytics-export-orders") + "?days=30",
            reverse("analytics-export-products") + "?days=30",
            reverse("analytics-export-customers") + "?days=30",
        ]

    def test_exports_require_login(self) -> None:
        for url in self.urls:
            r = self.client.get(url)
            self.assertIn(r.status_code, (301, 302))

    def test_customer_forbidden_or_hidden(self) -> None:
        self.client.login(username="customer1", password="pass12345")
        for url in self.urls:
            r = self.client.get(url)
            self.assertIn(r.status_code, (403, 404))

    @patch("analyticsapp.views.log_event")
    def test_ops_can_export_and_audit_called(self, mock_log_event) -> None:
        self.client.login(username="ops1", password="pass12345")

        for url in self.urls:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
            self.assertIn("text/csv", r.get("Content-Type", ""))
            cd = r.get("Content-Disposition", "")
            self.assertIn("attachment", cd)
            self.assertIn(".csv", cd)

        self.assertTrue(mock_log_event.called)

    @patch("analyticsapp.views.log_event")
    def test_admin_can_export_and_audit_called(self, mock_log_event) -> None:
        self.client.login(username="admin1", password="pass12345")

        for url in self.urls:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)

        self.assertTrue(mock_log_event.called)
