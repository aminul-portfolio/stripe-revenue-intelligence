from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch


class MonitoringSmokeTests(TestCase):
    def _login_admin(self) -> None:
        User = get_user_model()
        user = User.objects.create_user(
            username="admin_smoke",
            email="admin_smoke@example.com",
            password="pass12345",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(user)

    def test_monitoring_urls_resolve_or_are_protected(self):
        """
        Goal: prove monitoring endpoints exist and do not 500.

        This test is intentionally tolerant:
        - If an endpoint requires auth, we login and expect 200.
        - If an endpoint redirects (302) to login, that's acceptable.
        - We explicitly fail only on 500 or missing URL names.
        """
        candidates = [
            "monitoring:monitoring-issues",
        ]

        resolved_any = False
        last_error = None

        for name in candidates:
            try:
                url = reverse(name)
            except NoReverseMatch as e:
                last_error = e
                continue

            resolved_any = True

            # Try unauthenticated first
            resp = self.client.get(url)
            if resp.status_code == 500:
                self.fail(f"{name} returned 500")

            # If protected, login and retry
            if resp.status_code in (301, 302, 403):
                self._login_admin()
                resp2 = self.client.get(url)
                if resp2.status_code == 500:
                    self.fail(f"{name} returned 500 after login")

                # Accept 200 OK, or redirect patterns depending on your RBAC/login setup
                self.assertIn(resp2.status_code, (200, 301, 302, 403))

            else:
                self.assertIn(resp.status_code, (200, 301, 302, 403))

            break

        if not resolved_any:
            self.fail(
                "No monitoring URL names resolved. "
                "Add/confirm monitoring namespace + url names. "
                f"Last reverse error: {last_error}"
            )
