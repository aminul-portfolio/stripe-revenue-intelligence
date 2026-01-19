from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SubscriptionsSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s1",
            email="s1@example.com",
            password="pass12345",
        )

    def test_subscriptions_requires_login(self):
        """
        Subscriptions should not be publicly accessible.
        Accept 302 redirect to login or 403 depending on auth setup.
        """
        url = reverse("my-subscriptions")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 403))

    def test_subscriptions_page_renders_for_logged_in_user(self):
        """
        Logged-in user should be able to view subscriptions without 500.
        """
        self.client.force_login(self.user)
        url = reverse("my-subscriptions")
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 500)
        self.assertIn(resp.status_code, (200, 302, 403))
