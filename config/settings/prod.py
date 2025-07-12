import os

from .base import *

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False
