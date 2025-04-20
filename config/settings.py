import os
import sys
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", False) == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap4",
    "django_celery_beat",
    "phonenumber_field",
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_extensions",
    "drf_spectacular",
    "users",
]

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    # Включаем преобразование имен в camelCase
    "CAMELIZE_NAMES": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "static/"

STATICFILES_DIRS = (
    [os.path.join(BASE_DIR, "static")]
    if (
        os.path.exists(os.path.join(BASE_DIR, "static"))
        and os.listdir(os.path.join(BASE_DIR, "static"))
    )
    else []
)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
CRISPY_TEMPLATE_PACK = "bootstrap4"

LOGIN_URL = "/users/login/"

CACHE_ENABLED = os.getenv("CACHE_ENABLED") == "True"

if CACHE_ENABLED:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("LOCATION"),
        }
    }

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

AUTH_USER_MODEL = "users.User"

# Настройки для Celery

# URL-адрес брокера сообщений (Например, Redis,
# который по умолчанию работает на порту 6379)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")

# URL-адрес брокера результатов, также Redis
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

# Часовой пояс для работы Celery
CELERY_TIMEZONE = "Europe/Moscow"

# Флаг отслеживания выполнения задач
CELERY_TASK_TRACK_STARTED = True

# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 30 * 60

#  чтобы задачи не смешивались с другими проектами
CELERY_TASK_DEFAULT_QUEUE = "habit_tracker_queue"
CELERY_IGNORE_RESULT = True
#  для безопасности
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Настройки для Celery beat
# CELERY_BEAT_SCHEDULE = {
#     "task-name": {
#         "task": "myapp.tasks.task_name",
#         "schedule": timedelta(minutes=1),
# "schedule": crontab(hour=8, minute=0),  # Ежедневно в 8:00 утра
# },
# }


# Разрешаем CORS для localhost на разных портах
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Типичный порт для React-приложений
    "http://localhost:8000",  # Django development server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://130.193.54.21",
    "https://130.193.54.21",
    "http://130.193.54.21:8080",
]

# Доверенные источники для CSRF
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://130.193.54.21",
    "https://130.193.54.21",
    "http://130.193.54.21:8080",
]

# Отключаем разрешение для всех источников
CORS_ALLOW_ALL_ORIGINS = False

# Дополнительные настройки для разработки
CORS_ALLOW_CREDENTIALS = True


# CICD ([flake8])
# это нужно, чтобы при запуске тестов использовалась легкая SQLite, а не PostgreSQL

if "test" in sys.argv:
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    CELERY_TASK_ALWAYS_EAGER = True  # Выполнять задачи синхронно
    CELERY_TASK_EAGER_PROPAGATES = True  # Пропускать ошибки из задач
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",
        }
    }


# Настройки для сброса пароля
PASSWORD_RESET_SETTINGS = {
    # Путь для сброса пароля
    "PASSWORD_RESET_URL": "users/password-reset-confirm/{uid}/{token}/",
    # Тема письма
    "PASSWORD_RESET_EMAIL_SUBJECT": "Сброс пароля",
    # Текст письма
    "PASSWORD_RESET_EMAIL_MESSAGE": "Для сброса пароля перейдите по ссылке:",
    # Сообщение об успешной отправке
    "PASSWORD_RESET_SUCCESS_MESSAGE": "Инструкция по сбросу пароля отправлена на ваш email.",
    # Сообщение об ошибке
    "PASSWORD_RESET_ERROR_MESSAGE": "Пользователь не активен. Подтвердите email для восстановления пароля.",
}
