from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserRole

User = get_user_model()


class AnalyticsAccessTests(TestCase):
    def setUp(self):
        # Ensure permission exceptions become HTTP responses (403/404) rather than crashing tests.
        # Django supports raise_request_exception from modern versions; fallback is safe.
        try:
            self.client = Client(raise_request_exception=False)
        except TypeError:
            self.client = Client()

    def _mk_user(self, *, username: str, is_staff: bool, role: str):
        u = User.objects.create_user(username=username, password="pass12345")
        u.is_staff = is_staff
        u.save()

        # Your project likely auto-creates UserRole via a signal.
        # So get-or-create and update role safely.
        profile, created = UserRole.objects.get_or_create(
            user=u, defaults={"role": role}
        )
        if not created and profile.role != role:
            profile.role = role
            profile.save(update_fields=["role"])

        return u

    def test_dashboard_redirects_when_unauthenticated(self):
        resp = self.client.get(reverse("analytics-dashboard"))
        self.assertIn(resp.status_code, (301, 302))
        # Don't hardcode exact path; just confirm it is a login redirect.
        self.assertIn("login", resp["Location"].lower())

    def test_exports_redirect_when_unauthenticated(self):
        for name in (
            "analytics-export-orders",
            "analytics-export-products",
            "analytics-export-customers",
        ):
            resp = self.client.get(reverse(name) + "?days=30")
            self.assertIn(resp.status_code, (301, 302))
            self.assertIn("login", resp["Location"].lower())

    def test_dashboard_blocked_for_logged_in_non_staff(self):
        u = self._mk_user(username="cust1", is_staff=False, role="analyst")
        self.client.force_login(u)

        resp = self.client.get(reverse("analytics-dashboard"))
        # Logged in but non-staff => should be blocked (403 or 404 depending on your policy)
        self.assertIn(resp.status_code, (403, 404))

    def test_exports_blocked_for_logged_in_non_staff(self):
        u = self._mk_user(username="cust2", is_staff=False, role="ops")
        self.client.force_login(u)

        resp = self.client.get(reverse("analytics-export-orders") + "?days=30")
        self.assertIn(resp.status_code, (403, 404))

    def test_dashboard_allows_staff_analyst(self):
        u = self._mk_user(username="analyst1", is_staff=True, role="analyst")
        self.client.force_login(u)

        resp = self.client.get(reverse("analytics-dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_exports_allow_staff_ops(self):
        u = self._mk_user(username="ops1", is_staff=True, role="ops")
        self.client.force_login(u)

        resp = self.client.get(reverse("analytics-export-orders") + "?days=30")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("text/csv"))

        resp = self.client.get(reverse("analytics-export-products") + "?days=30")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("text/csv"))

        resp = self.client.get(reverse("analytics-export-customers") + "?days=30")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("text/csv"))

    def test_dashboard_blocked_for_staff_customer_role(self):
        u = self._mk_user(username="staffcust", is_staff=True, role="customer")
        self.client.force_login(u)

        resp = self.client.get(reverse("analytics-dashboard"))
        self.assertIn(resp.status_code, (403, 404))
