import os

# flake8: noqa
from .base import *
from dotenv import load_dotenv

load_dotenv()

# ALLOWED_HOSTS = [
#     "collection-agency-dev-142187143803.us-central1.run.app"
# ]
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
DEBUG = False

print("Using DEV settings")
print("ENV VARS: ", os.environ)
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
