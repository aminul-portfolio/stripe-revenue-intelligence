from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

CONTRACT_PATH = Path("docs/contracts/kpi_contract.json")


def _read_contract() -> dict:
    if not CONTRACT_PATH.exists():
        raise AssertionError(
            f"Missing contract file: {CONTRACT_PATH}. "
            "This file is the authoritative export header contract."
        )
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _csv_headers(response) -> list[str]:
    body = response.content.decode("utf-8", errors="replace")
    first_row = next(csv.reader(StringIO(body)))
    return first_row


class ExportContractTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user, _ = User.objects.get_or_create(
            username="contract_test_admin",
            defaults={
                "email": "contract-test@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        self.user.set_password("contract-pass-123")
        self.user.save()

        # Avoid DisallowedHost (your project blocks testserver in some contexts).
        self.client = Client(HTTP_HOST="localhost")
        ok = self.client.login(
            username="contract_test_admin", password="contract-pass-123"
        )
        assert ok is True

    def test_export_headers_match_contract(self) -> None:
        """
        Buyer-ready guarantee:
        Export CSV headers must match docs/contracts/kpi_contract.json exactly.
        This prevents silent drift between docs, UI, and downstream BI pipelines.
        """
        contract = _read_contract()
        exports: dict[str, list[str]] = contract["exports"]

        for export_name, expected_headers in exports.items():
            url = reverse(export_name)
            resp = self.client.get(url)

            self.assertEqual(
                resp.status_code, 200, f"{export_name} returned {resp.status_code}"
            )
            self.assertIn(
                "text/csv",
                (resp.get("Content-Type") or "").lower(),
                f"{export_name} not CSV",
            )

            actual_headers = _csv_headers(resp)
            self.assertEqual(
                actual_headers,
                expected_headers,
                (
                    f"{export_name} header drift.\n"
                    f"Expected: {expected_headers}\n"
                    f"Actual:   {actual_headers}\n"
                    f"URL: {url}"
                ),
            )
