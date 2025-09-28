# =====================================================================
# Production settings
# =====================================================================

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .base import *  # noqa: F403

# ---------------------------------------------------------------------
# Core / Debug
# ---------------------------------------------------------------------

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = False

# ---------------------------------------------------------------------
# Admins / Managers
# ---------------------------------------------------------------------

ADMINS = [("admin", os.getenv("DJANGO_ADMIN_EMAIL"))]
MANAGERS = ADMINS

# ---------------------------------------------------------------------
# Hosts & Origins
# ---------------------------------------------------------------------

ALLOWED_HOSTS = (
    os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if os.getenv("DJANGO_ALLOWED_HOSTS") else []
)

FRONTEND = os.getenv("FRONTEND")
CORS_ALLOWED_ORIGINS = [FRONTEND] if FRONTEND else []
CSRF_TRUSTED_ORIGINS = [FRONTEND] if FRONTEND else []

# ---------------------------------------------------------------------
# Auth / Redirects
# ---------------------------------------------------------------------

LOGIN_REDIRECT_URL = FRONTEND or "/"

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASS"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 60,
    }
}

# ---------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

# ---------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_DEFAULT_FROM_EMAIL")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ---------------------------------------------------------------------
# Security Headers / HTTPS
# ---------------------------------------------------------------------

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_CONTENT_TYPE_NOSNIFF = True
# https://wiki.mozilla.org/Security/Guidelines/Web_Security#HTTP_Strict_Transport_Security
SECURE_HSTS_SECONDS = 63072000  # 2 years
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ---------------------------------------------------------------------
# Cookies / CSRF / Session
# ---------------------------------------------------------------------

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = "__Secure-sessionid"

CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_NAME = "__Secure-csrftoken"

# ---------------------------------------------------------------------
# Storage / Static
# ---------------------------------------------------------------------

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------
# Sentry
# ---------------------------------------------------------------------

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,
)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment="production",
    integrations=[
        CeleryIntegration(),
        DjangoIntegration(),
        sentry_logging,
    ],
    send_default_pii=True,
    traces_sample_rate=0.5,
)
