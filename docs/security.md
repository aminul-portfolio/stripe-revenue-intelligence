# Security (Baseline)

This project ships with safe defaults for local development and tighter defaults for production.

## Local development
- `DEBUG=True` (default)
- Secure cookies and HSTS are not enforced.

## Production guidance
When `DEBUG=False`, the app enables:
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- HSTS enabled (`SECURE_HSTS_SECONDS=31536000`)
- `SECURE_CONTENT_TYPE_NOSNIFF=True`, `X_FRAME_OPTIONS=DENY`, `REFERRER_POLICY=same-origin`

## Secrets
Do not commit `.env`. Use environment variables or a secrets manager in production.
