import os

from .base import *


dev_domain = os.environ.get("DEV_CANONICAL_ROOT_DOMAIN", "localhost:8000")

SECRET_KEY = os.environ.get("DEV_SECRET_KEY", "o kawaii koto")
CANONICAL_ROOT_DOMAIN = dev_domain

DEBUG = False

ALLOWED_HOSTS = [dev_domain]

CANONICAL_SITE_NAME = dev_domain


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
SCRAPER_BLACKLIST_FILE = os.path.join(PARENT_DIR, "scraper_blacklist.json")
