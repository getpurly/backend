# =====================================================================
# Base settings
# =====================================================================

from pathlib import Path

from .blacklist import BLACKLIST

# ---------------------------------------------------------------------
# Paths / Directories
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------
# Admin Site
# ---------------------------------------------------------------------

ADMIN_SITE_HEADER = "Purly Admin"
ADMIN_SITE_INDEX_TITLE = "Site administration"
ADMIN_SITE_TITLE = "admin"

# ---------------------------------------------------------------------
# Security / Middleware Options
# ---------------------------------------------------------------------

CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------
# Installed Apps
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth_ui",
    "allauth",
    "allauth.account",
    "django_filters",
    "drf_spectacular",
    "rest_framework",
    "corsheaders",
    "widget_tweaks",
    "slippers",
    "purly.address",
    "purly.approval",
    "purly.project",
    "purly.requisition",
    "purly.user",
]

# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------

MIDDLEWARE = [
    "config.middleware.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# ---------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ---------------------------------------------------------------------
# URL / WSGI
# ---------------------------------------------------------------------

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {"custom_tags": "templatetags.custom_tags"},
        },
    },
]

# ---------------------------------------------------------------------
# Authentication / Users
# ---------------------------------------------------------------------

AUTH_USER_MODEL = "user.CustomUser"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

LOGOUT_REDIRECT_URL = "account_login"
LOGIN_URL = "account_login"

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# ---------------------------------------------------------------------
# Static Files
# ---------------------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [Path(BASE_DIR) / "static"]
STATIC_ROOT = Path(BASE_DIR) / "staticfiles"

# ---------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# App Constants
# ---------------------------------------------------------------------

MAX_REQUISITION_LINES = 250
MAX_SEQUENCE_NUMBER = 1000

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

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
    "root": {"level": "INFO", "handlers": ["console"]},
}

# ---------------------------------------------------------------------
# DRF / API
# ---------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/minute", "user": "1000/minute"},
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "config.exceptions.custom_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Purly API",
    "DESCRIPTION": "Purly: Purchase, Simply.",
    "VERSION": "Version 1",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------------
# Allauth
# ---------------------------------------------------------------------

ACCOUNT_ADAPTER = "config.adapters.CustomAccountAdapter"

ALLAUTH_UI_THEME = "forest"

ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Purly] "
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "account_email"

ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_USERNAME_BLACKLIST = BLACKLIST
ACCOUNT_USERNAME_MIN_LENGTH = 3
