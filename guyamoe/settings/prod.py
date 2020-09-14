import os

from .base import *


SETTINGS_ENV = "prod"

CANONICAL_ROOT_DOMAIN = "guya.moe"
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "ALLOW"

DEBUG = False

ALLOWED_HOSTS = [
    "guya.moe",
    "www.guya.moe",
    "kaguya.guya.moe",
    "www.kaguya.guya.moe",
    "ka.guya.moe",
    "www.ka.guya.moe",
    "ice.guya.moe",
    "www.ice.guya.moe",
    "baka.guya.moe",
    "www.baka.guya.moe",
    "trash.guya.moe",
    "www.trash.guya.moe",
    "dog.guya.moe",
    "www.dog.guya.moe",
    "kuu.guya.moe",
    "www.kuu.guya.moe",
    "localhost",
]

CANONICAL_SITE_NAME = "guya.moe"

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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASS"),
        "HOST": "localhost",
        "PORT": "",
    }
}

OCR_SCRIPT_PATH = os.path.join(PARENT_DIR, "ocr_tool.sh")
