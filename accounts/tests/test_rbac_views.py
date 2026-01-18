from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserRole

User = get_user_model()


class RBACTestCase(TestCase):
    # Update these if your URLs differ
    ANALYTICS_DASHBOARD_PATH = "/analytics/dashboard/"
    ANALYTICS_EXPORT_PATH = "/analytics/export/orders/?days=30"
    MONITORING_ISSUES_PATH = "/monitoring/issues/"

    def setUp(self):
        self.customer = User.objects.create_user(username="cust", password="pass")
        UserRole.objects.update_or_create(
            user=self.customer, defaults={"role": "customer"}
        )

        self.analyst = User.objects.create_user(
            username="analyst", password="pass", is_staff=True
        )
        UserRole.objects.update_or_create(
            user=self.analyst, defaults={"role": "analyst"}
        )

        self.ops = User.objects.create_user(
            username="ops", password="pass", is_staff=True
        )
        UserRole.objects.update_or_create(user=self.ops, defaults={"role": "ops"})

    def test_analytics_requires_login(self):
        r = self.client.get(self.ANALYTICS_DASHBOARD_PATH)
        self.assertEqual(r.status_code, 302)

    def test_customer_forbidden_analytics(self):
        self.client.login(username="cust", password="pass")
        r = self.client.get(self.ANALYTICS_DASHBOARD_PATH)
        self.assertEqual(r.status_code, 403)

    def test_ops_allowed_analytics(self):
        self.client.login(username="ops", password="pass")
        r = self.client.get(self.ANALYTICS_DASHBOARD_PATH)
        self.assertEqual(r.status_code, 200)

    def test_analyst_allowed_analytics(self):
        self.client.login(username="analyst", password="pass")
        r = self.client.get(self.ANALYTICS_DASHBOARD_PATH)
        self.assertEqual(r.status_code, 200)

    def test_export_orders_csv_allows_ops_and_analyst(self):
        self.client.login(username="ops", password="pass")
        r = self.client.get(self.ANALYTICS_EXPORT_PATH)
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r["Content-Type"])

        self.client.login(username="analyst", password="pass")
        r = self.client.get(self.ANALYTICS_EXPORT_PATH)
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r["Content-Type"])

    def test_monitoring_ops_or_analyst(self):
        self.client.login(username="cust", password="pass")
        r = self.client.get(self.MONITORING_ISSUES_PATH)
        self.assertEqual(r.status_code, 403)

        self.client.login(username="ops", password="pass")
        r = self.client.get(self.MONITORING_ISSUES_PATH)
        self.assertEqual(r.status_code, 200)

        self.client.login(username="analyst", password="pass")
        r = self.client.get(self.MONITORING_ISSUES_PATH)
        self.assertEqual(r.status_code, 200)
