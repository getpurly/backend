import os

from .base import *  # noqa: F403

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False
