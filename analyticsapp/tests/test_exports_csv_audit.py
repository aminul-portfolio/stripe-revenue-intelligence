from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.services.roles import set_role

User = get_user_model()


class ExportAuditTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.analyst = User.objects.create_user(
            username="analyst1",
            email="analyst1@example.com",
            password="pass12345",
        )
        set_role(self.analyst, "analyst")

        self.customer = User.objects.create_user(
            username="cust1",
            email="cust1@example.com",
            password="pass12345",
        )
        set_role(self.customer, "customer")

        self.urls = [
            reverse("analytics-export-kpi-summary") + "?days=30",
            reverse("analytics-export-orders") + "?days=30",
            reverse("analytics-export-products") + "?days=30",
            reverse("analytics-export-customers") + "?days=30",
        ]

    def test_customer_denied(self) -> None:
        self.client.login(username="cust1", password="pass12345")
        for url in self.urls:
            r = self.client.get(url)
            self.assertIn(r.status_code, (403, 404))

    @patch("analyticsapp.views.log_event")
    def test_analyst_can_export_and_is_audited(self, mock_log_event) -> None:
        self.client.login(username="analyst1", password="pass12345")
        for url in self.urls:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
            self.assertIn("text/csv", r.get("Content-Type", ""))

        self.assertTrue(mock_log_event.called)
