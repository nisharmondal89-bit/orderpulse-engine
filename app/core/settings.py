import os
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR= Path(__file__).resolve().parent.parent
SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG=os.getenv("DEBUG", "False").lower()=="true"
ALLOWED_HOSTS=["*"]

INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django_prometheus",
        "rest_framework",
        "orders",
        ]

MIDDLEWARE=["django.middleware.common.CommonMiddleware",
            "django_prometheus.middleware.PrometheusBeforeMiddleware",
            "django_prometheus.middleware.PrometheusAfterMiddleware"
            ]
ROOT_URLCONF="core.urls"
WSGI_APPLICATION="core.wsgi.application"


db_url=urlparse(os.getenv("DATABASE_URL", "postgres://appuser:apppassword@localhost:5432/orderpulse"))
DATABASES= {
        "default": {
            "ENGINE": "django_prometheus.db.backends.postgresql",
            "NAME": db_url.path[1:],
            "USER": db_url.username,
            "PASSWORD": db_url.password,
            "HOST": db_url.hostname,
            "PORT": db_url.port or 5432,
            }
        }

MONGO_URI= os.getenv("MONGO_URI", "mongodb://localhost:27017/")
CELERY_BROKER_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND= CELERY_BROKER_URL
DEFAULT_AUTO_FIELD= "django.db.models.BigAutoField"


