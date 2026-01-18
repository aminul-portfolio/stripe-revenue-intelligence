# PureLaka Enterprise — Deployment Notes

This document describes environment configuration, deployment steps, and production hardening notes for:
`PureLaka_Commerce_Platform_LAUNCH_READY`.

## 1) Environments

Supported:
- Local dev: Windows + venv (current)
- Production: recommended Linux + Postgres
- SQLite is acceptable for demos, but not recommended for real production concurrency.

## 2) Environment variables (must match settings.py)

Your `settings.py` reads these variable names:

### Core Django
- `SECRET_KEY` (required in production)
- `DEBUG` (`True/False`)
- `ALLOWED_HOSTS` (comma-separated)
- `CSRF_TRUSTED_ORIGINS` (comma-separated, include https origins)

### Stripe (Payments + Subscriptions)
- `PAYMENTS_USE_STRIPE` (`0/1` or `true/false/yes/no` based on parsing)
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DEFAULT_STRIPE_PRICE_ID` (if your subscription creation flow relies on it)

Operational notes:
- Webhook endpoint: `/payments/webhook/`
- Keep signature verification enabled in production.

## 3) Recommended production database

Local uses SQLite:
- `db.sqlite3`

For production, use Postgres (recommended):
- add a database URL strategy (e.g., `DATABASE_URL`) later when you choose a platform
- or configure Postgres via platform settings and update `DATABASES`

## 4) Pre-deploy checklist (must-do)

### 4.1 Set production env vars
Minimum:
- `DEBUG=False`
- `SECRET_KEY=<strong-secret>`
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- `CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`

If using Stripe in production:
- `PAYMENTS_USE_STRIPE=1`
- `STRIPE_PUBLISHABLE_KEY=...`
- `STRIPE_SECRET_KEY=...`
- `STRIPE_WEBHOOK_SECRET=...`
- `DEFAULT_STRIPE_PRICE_ID=...`

### 4.2 Apply migrations
```powershell
python manage.py migrate
