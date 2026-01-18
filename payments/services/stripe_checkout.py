import stripe
from django.conf import settings


def init_stripe():
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(*, order, request) -> dict:
    """
    Creates a Stripe Checkout Session for an Order.
    Uses the order total as a single line item (simple & robust).
    """
    init_stripe()

    success_url = request.build_absolute_uri(f"/payments/success/{order.id}/")
    cancel_url = request.build_absolute_uri(f"/payments/cancel/{order.id}/")

    amount_pennies = int(order.total * 100)

    session = stripe.checkout.Session.create(
        mode="payment",
        metadata={"order_id": str(order.id)},
        client_reference_id=str(order.id),
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {"name": f"Order #{order.id}"},
                    "unit_amount": amount_pennies,
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=order.email,
    )
    return session
