from pathlib import Path

from .blacklist import BLACKLIST

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ADMIN_SITE_HEADER = "Purly Admin"
ADMIN_SITE_INDEX_TITLE = "Site administration"
ADMIN_SITE_TITLE = "admin"

ADMINS = [("admin", "admin@example.com")]
MANAGERS = ADMINS

CORS_ALLOW_CREDENTIALS = True

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

MIDDLEWARE = [
    "config.middleware.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {"custom_tags": "templatetags.custom_tags"},
        },
    },
]

AUTH_USER_MODEL = "user.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGOUT_REDIRECT_URL = "account_login"
LOGIN_URL = "account_login"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [Path(BASE_DIR) / "static"]
STATIC_ROOT = Path(BASE_DIR) / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MAX_REQUISITION_LINES = 250

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
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
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

ALLAUTH_UI_THEME = "forest"

ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Purly] "
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "account_email"

ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]

ACCOUNT_PRESERVE_USERNAME_CASING = False

ACCOUNT_USERNAME_BLACKLIST = BLACKLIST
ACCOUNT_USERNAME_MIN_LENGTH = 3
