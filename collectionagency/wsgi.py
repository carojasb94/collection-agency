"""
WSGI config for collectionagency project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


ENV = os.getenv("ENV", "dev")
settings_module = f"collectionagency.settings.{ENV}"

logger.info(f"Loading {settings_module} config.")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_wsgi_application()
