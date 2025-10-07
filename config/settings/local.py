# =====================================================================
# Local settings
# =====================================================================

from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE

# ---------------------------------------------------------------------
# Core / Debug
# ---------------------------------------------------------------------

SECRET_KEY = "hyBhCDX0pa9fi9XE3zLODw850fcjEaqA8tXaXzKYxdiJ9YcwyV5o33BJqGRDFqDi"  # noqa: S105
DEBUG = True

# ---------------------------------------------------------------------
# Admins / Managers
# ---------------------------------------------------------------------

ADMINS = [("admin", "admin@localhost")]
MANAGERS = ADMINS

# ---------------------------------------------------------------------
# Hosts & Origins
# ---------------------------------------------------------------------

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

FRONTEND = "http://localhost:5173"
CORS_ALLOWED_ORIGINS = [FRONTEND] if FRONTEND else []
CSRF_TRUSTED_ORIGINS = [FRONTEND] if FRONTEND else []

# ---------------------------------------------------------------------
# Auth / Redirects
# ---------------------------------------------------------------------

LOGIN_REDIRECT_URL = FRONTEND or "/"

# ---------------------------------------------------------------------
# Apps / Middleware (local-only additions)
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    *INSTALLED_APPS[:5],
    "whitenoise.runserver_nostatic",
    *INSTALLED_APPS[5:],
    "silk",
]

MIDDLEWARE += [
    "silk.middleware.SilkyMiddleware",
]

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dev",
        "USER": "dev",
        "PASSWORD": "dev",
        "HOST": "192.168.1.130",
        "PORT": "5436",
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 60,
    }
}

# ---------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------

REDIS_URL = "redis://:dev@192.168.1.130:6379/0"

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

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "noreply@localhost"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ---------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
