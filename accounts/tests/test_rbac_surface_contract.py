from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserRole

User = get_user_model()


class TestRBACSurfaceContract(TestCase):
    """
    Contract-level RBAC tests to prevent accidental exposure.

    We intentionally accept 403 or 404 for denied authenticated users,
    because this repo uses "hidden 404" in some places by design.
    """

    def setUp(self) -> None:
        self.customer = User.objects.create_user(
            username="cust_rbac", email="cust@example.com", password="pass12345"
        )
        UserRole.objects.update_or_create(
            user=self.customer, defaults={"role": "customer"}
        )

        self.analyst = User.objects.create_user(
            username="analyst_rbac",
            email="analyst@example.com",
            password="pass12345",
            is_staff=True,
        )
        UserRole.objects.update_or_create(
            user=self.analyst, defaults={"role": "analyst"}
        )

        self.ops = User.objects.create_user(
            username="ops_rbac",
            email="ops@example.com",
            password="pass12345",
            is_staff=True,
        )
        UserRole.objects.update_or_create(user=self.ops, defaults={"role": "ops"})

        self.admin = User.objects.create_user(
            username="admin_rbac",
            email="admin@example.com",
            password="pass12345",
            is_staff=True,
            is_superuser=True,
        )
        # If your code uses UserRole for admin paths, keep it explicit.
        UserRole.objects.update_or_create(user=self.admin, defaults={"role": "admin"})

        self.analytics_urls = [
            reverse("analytics-dashboard") + "?days=7",
            reverse("analytics-export-kpi-summary"),
            reverse("analytics-export-orders"),
            reverse("analytics-export-products"),
            reverse("analytics-export-customers"),
        ]
        self.monitoring_url = "/monitoring/issues/"

    def _assert_login_redirect(self, response) -> None:
        # Avoid brittle assumptions about exact login URL; just require redirect.
        self.assertIn(response.status_code, (301, 302))

    def _assert_denied(self, response) -> None:
        self.assertIn(response.status_code, (403, 404))

    def test_anon_is_redirected_from_protected_surfaces(self) -> None:
        for url in self.analytics_urls + [self.monitoring_url]:
            r = self.client.get(url)
            self._assert_login_redirect(r)

    def test_customer_is_denied_everywhere(self) -> None:
        self.client.login(username="cust_rbac", password="pass12345")
        for url in self.analytics_urls + [self.monitoring_url]:
            r = self.client.get(url)
            self._assert_denied(r)

    def test_analyst_is_allowed_analytics_and_monitoring(self) -> None:
        self.client.login(username="analyst_rbac", password="pass12345")
        for url in self.analytics_urls:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)

        r = self.client.get(self.monitoring_url)
        self.assertEqual(r.status_code, 200)

    def test_ops_is_allowed_analytics_and_monitoring(self) -> None:
        self.client.login(username="ops_rbac", password="pass12345")
        for url in self.analytics_urls:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)

        r = self.client.get(self.monitoring_url)
        self.assertEqual(r.status_code, 200)

    def test_admin_is_allowed_everywhere(self) -> None:
        self.client.login(username="admin_rbac", password="pass12345")
        for url in self.analytics_urls + [self.monitoring_url]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
