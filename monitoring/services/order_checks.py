from orders.models import Order
from monitoring.models import DataQualityIssue


def check_order_state_integrity():
    for o in Order.objects.filter(status="paid", stripe_payment_intent=""):
        DataQualityIssue.objects.get_or_create(
            issue_type="order_state",
            reference_id=str(o.id),
            defaults={
                "description": "Paid order missing Stripe PaymentIntent reference."
            },
        )
