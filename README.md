# PureLaka Commerce Platform

Enterprise-grade Django e-commerce + analytics platform (portfolio flagship).

## Feature Set (implemented)
- Products & variants, categories, images
- Session cart + checkout flow
- Orders + order items (pending → paid → fulfilled/cancelled)
- Stripe-ready Payments (PaymentIntent) with optional Mock mode for local development
- Subscriptions (Stripe-ready scaffold) + churn analytics
- Wishlist + wishlist→purchase funnel analytics
- Analytics dashboard (KPIs + Plotly charts), date filters (7/30/90) and CSV export
- Data Quality Monitoring (payment/order mismatch, invalid order state, negative stock)
- Audit Trail (event logging) for payments, status changes, admin actions
- Role-Based Access Control (Admin / Analyst / Ops)

## Quickstart (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open:
- Home: http://127.0.0.1:8000/
- Products: http://127.0.0.1:8000/products/
- Cart: http://127.0.0.1:8000/cart/
- Checkout: http://127.0.0.1:8000/orders/checkout/
- Analytics: http://127.0.0.1:8000/analytics/dashboard/
- Monitoring: http://127.0.0.1:8000/monitoring/issues/
- Admin: http://127.0.0.1:8000/admin/

## Environment
Copy `.env.example` to `.env`. Stripe is optional for local development (`PAYMENTS_USE_STRIPE=False` uses a safe mock flow).

## Default demo users (after seed_demo)
- admin / admin12345 (superuser)
- analyst / analyst12345 (staff + analyst role)
- ops / ops12345 (staff + ops role)

