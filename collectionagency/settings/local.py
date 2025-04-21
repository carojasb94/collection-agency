"""Local settings"""

import os

# flake8: noqa
from .base import *

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
DEBUG = True

print("Using LOCAL settings")

# docker-compose db
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ.get("DB_PORT", "5432"),
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
    }
}
