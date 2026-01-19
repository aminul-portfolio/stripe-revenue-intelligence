from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class WishlistSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="w1",
            email="w1@example.com",
            password="pass12345",
        )

    def test_wishlist_requires_login(self):
        """
        Wishlist should not be publicly accessible.
        Accept 302 redirect to login or 403 depending on auth setup.
        """
        url = reverse("my-wishlist")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 403))

    def test_wishlist_page_renders_for_logged_in_user(self):
        """
        Logged-in user should be able to view wishlist without 500.
        """
        self.client.force_login(self.user)
        url = reverse("my-wishlist")
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 500)
        self.assertIn(resp.status_code, (200, 302, 403))
