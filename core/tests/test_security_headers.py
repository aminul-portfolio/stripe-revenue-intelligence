from django.test import TestCase
from django.urls import reverse


class SecurityHeadersTests(TestCase):
    def test_home_sets_basic_security_headers(self):
        resp = self.client.get(reverse("home"))
        # X-Frame-Options is set by middleware + settings
        self.assertIn("X-Frame-Options", resp.headers)
        # nosniff protection
        self.assertIn("X-Content-Type-Options", resp.headers)
