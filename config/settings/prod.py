# =====================================================================
# Production settings
# =====================================================================

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa: F403
from .base import INSTALLED_APPS

# ---------------------------------------------------------------------
# Core / Debug
# ---------------------------------------------------------------------

DEBUG = False

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

SITE_NAME = os.getenv("DJANGO_SITE_NAME")
SITE_URL = os.getenv("DJANGO_SITE_URL")

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

REDIS_URL = "redis://:{password}@{host}:{port}/0".format(
    password=os.getenv("REDIS_PASS"),
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# ---------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------

EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"

DEFAULT_FROM_EMAIL = os.getenv("DJANGO_DEFAULT_FROM_EMAIL")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_SES"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_KEY_SES"),
        "region_name": os.getenv("AWS_REGION"),
    },
}

# ---------------------------------------------------------------------
# Installed Apps
# ---------------------------------------------------------------------

INSTALLED_APPS += ["anymail"]

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

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

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
        RedisIntegration(),
        sentry_logging,
    ],
    send_default_pii=True,
    traces_sample_rate=0.5,
)
