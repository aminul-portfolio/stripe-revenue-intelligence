# PureLaka Enterprise — Deployment Guide (Production-Shaped)

This document describes environment configuration, deployment steps, and production hardening notes for:
`stripe-revenue-intelligence` (PureLaka / Revenue Intelligence for Stripe Commerce).

Goal: a reviewer (or future you) can deploy in a “production-shaped” way and run the required deploy checks.

---

## 1) Supported environments

- Local dev: Windows + venv + SQLite (current dev workflow)
- Production-shaped: Linux + Postgres (recommended)
- Demo-only: SQLite is acceptable for local demos, but **not recommended** for real production concurrency.

---

## 2) Environment variables (as used by the project)

Your Django settings require these variables (names must match what your settings read).

### 2.1 Core Django
- `SECRET_KEY` (**required** in production)
- `DEBUG` (`True/False`)
- `ALLOWED_HOSTS` (comma-separated)
- `CSRF_TRUSTED_ORIGINS` (comma-separated, include `https://` origins)

### 2.2 Database
- **Local dev:** SQLite (default)
- **Production:** Postgres via `DATABASE_URL` or explicit `DATABASES` settings (platform-dependent)
  - If your repo currently uses explicit `DATABASES`, configure Postgres by updating that section or by adding `DATABASE_URL` support as part of milestone M4.

### 2.3 Stripe (Payments + Subscriptions)
- `PAYMENTS_USE_STRIPE` (`0/1` or truthy/falsey)
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DEFAULT_STRIPE_PRICE_ID` (if subscriptions rely on a default price)

Operational notes:
- Webhook endpoint: `/payments/webhook/`
- Keep Stripe signature verification enabled in production.

---

## 3) Pre-deploy checklist (must-do)

### 3.1 Set production env vars
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

### 3.2 Run the deploy check (required “senior signal”)
From the repo root:
```powershell
python manage.py check --deploy
