import os

from .base import *


dev_domain = os.environ.get("DEV_CANONICAL_ROOT_DOMAIN", "localhost:8000")

SECRET_KEY = os.environ.get("DEV_SECRET_KEY", "o kawaii koto")
CANONICAL_ROOT_DOMAIN = dev_domain

DEBUG = False

ALLOWED_HOSTS = [dev_domain]

CANONICAL_SITE_NAME = dev_domain

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(PARENT_DIR, "guyamoe.log"),
            "maxBytes": 1024 * 1024 * 100,  # 100 mb
        }
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "WARNING", "propagate": True,},
    },
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache",}}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DEV_DB_NAME"),
        "USER": os.environ.get("DEV_DB_USER"),
        "PASSWORD": os.environ.get("DEV_DB_PASS"),
        "HOST": "localhost",
        "PORT": "",
    }
}

OCR_SCRIPT_PATH = os.path.join(PARENT_DIR, "ocr_tool.sh")
