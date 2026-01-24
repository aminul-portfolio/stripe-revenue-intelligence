# PureLaka Commerce Platform

![CI](https://github.com/aminul-portfolio/stripe-revenue-intelligence/actions/workflows/ci.yml/badge.svg)

Enterprise-grade Django e-commerce + analytics platform (portfolio flagship).

## Fast verification (reviewers)

- Acceptance Matrix (claims → code/tests/manual checks): [`docs/acceptance_matrix.md`](docs/acceptance_matrix.md)
- Status / milestone tracking: `docs/STATUS.md`
- Proof index: `docs/CONTRACTS_AND_PROOFS.md`

## Feature Set (implemented)

- Products & variants, categories, images
- Session cart + checkout flow
- Orders + order items (pending → paid → fulfilled/canceled)
- Stripe-ready Payments (PaymentIntent) with optional Mock mode for local development
- Subscriptions (Stripe-ready scaffold) + churn analytics
- Wishlist + wishlist→purchase funnel analytics
- Analytics dashboard (KPIs + Plotly charts), date filters (7/30/90) and CSV export
- Data Quality Monitoring (payment/order mismatch, invalid order state, negative stock)
- Audit Trail (event logging) for payments, status changes, admin actions
- Role-Based Access Control (Admin / Analyst / Ops)

## Requirements

This repo uses pip-tools lockfiles for deterministic installs:

- Inputs (human-edited): `requirements.in`, `requirements-dev.in`
- Locks (generated): `requirements.txt`, `requirements-dev.txt`

For development and CI parity, install `requirements-dev.txt`.

## Quickstart (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
