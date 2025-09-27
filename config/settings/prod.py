import os

import sentry_sdk

from .base import *  # noqa: F403

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    send_default_pii=True,
)
