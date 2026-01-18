from orders.models import Order
from monitoring.models import DataQualityIssue


def _ensure_issue(issue_type: str, reference_id: str, description: str) -> None:
    """
    Create issue if not exists. Keeps one issue per (issue_type, reference_id)
    due to model unique_together.
    """
    DataQualityIssue.objects.get_or_create(
        issue_type=issue_type,
        reference_id=reference_id,
        defaults={"description": description},
    )


def check_payment_reconciliation() -> None:
    """
    Enterprise payment reconciliation rules:

    1) Mock payments:
       - Order paid in demo/mock mode must be ignored by Stripe reconciliation checks.
       - Expected markers:
           stripe_payment_intent == "mock" AND stripe_charge_id == "mock"

    2) Stripe payments:
       - If stripe_payment_intent startswith "pi_", it is a Stripe order.
       - A Stripe-paid order should have a stripe_charge_id (or at minimum, intent id).
       - Missing charge id indicates webhook incomplete or event processing failure.

    3) Non-Stripe paid orders:
       - If an order is paid but has no Stripe refs and is not mock, flag as payment_mismatch
         (suspicious state) unless you explicitly support another payment provider.
    """

    qs = Order.objects.filter(status="paid")

    for o in qs:
        ref = f"order:{o.id}"

        intent = (o.stripe_payment_intent or "").strip()
        charge = (o.stripe_charge_id or "").strip()

        # ✅ Mock mode guard (no false positives)
        is_mock_order = (intent == "mock") or (charge == "mock")
        if is_mock_order:
            # Mock orders are valid demo states; do not create issues
            continue

        # ✅ Stripe order detection
        is_stripe_order = intent.startswith("pi_")

        if is_stripe_order:
            # Stripe-paid order missing charge id => webhook incomplete
            if not charge:
                _ensure_issue(
                    issue_type="missing_stripe_ref",
                    reference_id=ref,
                    description="Paid Stripe order missing stripe_charge_id (webhook may be incomplete).",
                )
        else:
            # Paid order not Stripe and not mock => suspicious (or alternative provider not modelled)
            if not intent and not charge:
                _ensure_issue(
                    issue_type="payment_mismatch",
                    reference_id=ref,
                    description="Paid order has no Stripe references and is not marked as mock.",
                )
