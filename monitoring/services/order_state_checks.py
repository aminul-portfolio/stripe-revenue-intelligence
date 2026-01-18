from orders.models import Order
from monitoring.models import DataQualityIssue


def check_invalid_order_states() -> None:
    """
    Enterprise order-state rules (NO false positives):

    1) Paid order must have proof of payment:
       - Stripe-paid: stripe_payment_intent startswith 'pi_' must exist
       - Mock-paid: stripe_payment_intent == 'mock' and stripe_charge_id == 'mock' is valid
       - If you later add other providers, extend this detection.

    2) Fulfilled order must be paid (and must have payment proof).

    3) Cancelled order should not be fulfilled; optional checks can be added later.
    """

    qs = Order.objects.all().only(
        "id", "status", "stripe_payment_intent", "stripe_charge_id"
    )

    for o in qs:
        ref = f"order:{o.id}"

        intent = (o.stripe_payment_intent or "").strip()
        charge = (o.stripe_charge_id or "").strip()

        is_mock_paid = (intent == "mock") or (charge == "mock")
        is_stripe_paid = intent.startswith("pi_")

        # --- Rule A: PAID must have valid payment proof ---
        if o.status == "paid":
            # valid paid states
            if is_mock_paid:
                continue
            if is_stripe_paid:
                # Stripe should at least have intent; charge may arrive via webhook later
                if not intent:
                    DataQualityIssue.objects.get_or_create(
                        issue_type="invalid_order_state",
                        reference_id=ref,
                        defaults={
                            "description": "Paid Stripe order missing Stripe PaymentIntent reference."
                        },
                    )
                continue

            # Paid but no known payment proof (not stripe, not mock)
            if not intent and not charge:
                DataQualityIssue.objects.get_or_create(
                    issue_type="invalid_order_state",
                    reference_id=ref,
                    defaults={
                        "description": "Order is paid but has no payment references."
                    },
                )

        # --- Rule B: FULFILLED must be PAID + valid payment proof ---
        if o.status == "fulfilled":
            if not (is_mock_paid or is_stripe_paid):
                DataQualityIssue.objects.get_or_create(
                    issue_type="invalid_order_state",
                    reference_id=ref,
                    defaults={
                        "description": "Order is fulfilled but has no valid payment proof."
                    },
                )

        # You can add more rules later (cancelled with charge, etc.)
