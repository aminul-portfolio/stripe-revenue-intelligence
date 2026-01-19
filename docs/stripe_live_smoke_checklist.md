# Stripe Live Smoke Checklist (Manual)

Purpose: Verify Stripe mode end-to-end in a safe, repeatable way.
This is intentionally manual and is NOT part of CI.

## Preconditions

- You have a Stripe account (test mode is fine).
- `.env` contains:
  - `PAYMENTS_USE_STRIPE=1`
  - `STRIPE_SECRET_KEY=...`
  - `STRIPE_PUBLISHABLE_KEY=...`
  - `STRIPE_WEBHOOK_SECRET=...`
- Stripe CLI installed and authenticated:
  - `stripe login`

## Safety controls

- Use Stripe test mode keys only.
- Use a separate test product / price IDs.
- Use small test payments only.

## Steps

### 1) Start app + confirm Stripe mode enabled

Run:

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
