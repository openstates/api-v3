import os
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://8b48c86eab184725896f0824c123a07d@o94516.ingest.sentry.io/5388471",
    integrations=[DjangoIntegration()],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.environ.get("DEBUG", "true").lower() == "false":
    DEBUG = False
    SECRET_KEY = os.environ["SECRET_KEY"]
else:
    DEBUG = True
    SECRET_KEY = "not-a-real-secret"


DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgis://openstates:openstates@db:5432/openstatesorg"
)
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
CONN_MAX_AGE = 60


ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = ["openstates.data", "api"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "web.wsgi.application"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = False
USE_TZ = True
STATIC_URL = "/static/"
