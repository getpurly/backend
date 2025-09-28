from .base import *  # noqa: F403

SECRET_KEY = "hyBhCDX0pa9fi9XE3zLODw850fcjEaqA8tXaXzKYxdiJ9YcwyV5o33BJqGRDFqDi"  # noqa: S105

DEBUG = True

ADMINS = [("admin", "admin@localhost")]
MANAGERS = ADMINS

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

FRONTEND = "http://localhost:5173"

CORS_ALLOWED_ORIGINS = [FRONTEND] if FRONTEND else []

CSRF_TRUSTED_ORIGINS = [FRONTEND] if FRONTEND else []

LOGIN_REDIRECT_URL = FRONTEND or "/"

INSTALLED_APPS = [*INSTALLED_APPS[:5], "whitenoise.runserver_nostatic", *INSTALLED_APPS[5:], "silk"]  # noqa: F405

MIDDLEWARE += [  # noqa: F405
    "silk.middleware.SilkyMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dev",
        "USER": "dev",
        "PASSWORD": "dev",
        "HOST": "192.168.1.130",
        "PORT": "5436",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@localhost"

SITE_NAME = "localhost"
SITE_URL = "http://localhost:8000"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}
