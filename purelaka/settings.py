from pathlib import Path
import os

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)

# Accept both common env names to avoid CI/local mismatch.
SECRET_KEY = (
    os.getenv("DJANGO_SECRET_KEY")
    or os.getenv("SECRET_KEY")
    or "dev-secret-key-change-me"
)

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

# Developer-friendly defaults (does not affect production if DEBUG=False)
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts.apps.AccountsConfig",
    "products",
    "cart",
    "orders",
    "payments",
    "subscriptions",
    "wishlist",
    "analyticsapp",
    "monitoring",
    "audit",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "purelaka.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.user_role",
                "cart.context_processors.cart_summary",
                "core.context_processors.payments_flags",
            ],
        },
    }
]

WSGI_APPLICATION = "purelaka.wsgi.application"
ASGI_APPLICATION = "purelaka.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 30},
    }
}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Stripe config (safe defaults for CI/tests when PAYMENTS_USE_STRIPE=0)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
DEFAULT_STRIPE_PRICE_ID = os.getenv("DEFAULT_STRIPE_PRICE_ID", "")

PAYMENTS_USE_STRIPE = os.getenv("PAYMENTS_USE_STRIPE", "0").lower() in (
    "1",
    "true",
    "yes",
)

# Fail-fast only when Stripe is enabled
if PAYMENTS_USE_STRIPE:
    missing = [
        name
        for name, value in {
            "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY,
            "STRIPE_WEBHOOK_SECRET": STRIPE_WEBHOOK_SECRET,
            "STRIPE_PUBLISHABLE_KEY": STRIPE_PUBLISHABLE_KEY,
        }.items()
        if not value
    ]
    if missing:
        raise ImproperlyConfigured(
            "PAYMENTS_USE_STRIPE=1 but missing required env vars: " + ", ".join(missing)
        )

LOGIN_REDIRECT_URL = "/account/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"

# ----------------------------
# Security baseline (M3)
# ----------------------------
# Keep dev/CI safe and simple; tighten automatically when DEBUG=False.

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies and transport security (only enforced when DEBUG=False)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Reasonable browser protections
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "same-origin"

# HSTS only when DEBUG=False (so localhost isn’t affected)
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False if DEBUG else True
SECURE_HSTS_PRELOAD = False if DEBUG else True
