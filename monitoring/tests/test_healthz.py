from django.test import TestCase


class HealthzTests(TestCase):
    def test_healthz_returns_200_and_db_true(self):
        resp = self.client.get("/monitoring/healthz/")
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["checks"]["db"])
