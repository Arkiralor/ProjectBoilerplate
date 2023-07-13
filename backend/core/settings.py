from datetime import datetime, timedelta
from pathlib import Path
import redis
from os import path, makedirs, environ

from core.apps import DEFAULT_APPS, THIRD_PARTY_APPS, CUSTOM_APPS
from core.cron_classes import JOB_HANDLER_APP_CRON, MIDDLEWARE_APP_CRON, USER_APP_CRON
from core.middleware import DEFAULT_MIDDLEWARE, THIRD_PARTY_MIDDLEWARE, CUSTOM_MIDDLEWARE
from core.rq_constants import JobQ

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = environ.get("SECRET_KEY", "t3mp0r4ry-s3cre4-k3y")

DEBUG = eval(environ.get("DEBUG", "False"))
ENV_TYPE = environ.get("ENV_TYPE", "PROD").lower()
MAX_ITEMS_PER_PAGE = 15

ALLOWED_HOSTS = environ.get("ALLOWED_HOSTS", "").split(", ")

INSTALLED_APPS = DEFAULT_APPS+THIRD_PARTY_APPS+CUSTOM_APPS
MIDDLEWARE = DEFAULT_MIDDLEWARE+THIRD_PARTY_MIDDLEWARE+CUSTOM_MIDDLEWARE

ROOT_URLCONF = 'core.urls'

APP_NAME = environ.get("APP_NAME", "")
DOMAIN_URL = environ.get("DOMAIN_URL", "")
OWNER_EMAIL = environ.get("OWNER_EMAIL", f"owner@{APP_NAME}.com")
CONTACT_EMAIL = environ.get("CONTACT_EMAIL", f"contact@{APP_NAME}.com")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ['DB_NAME'],
        'HOST': environ['DB_HOST'],
        'PORT': environ['DB_PORT'],
        'USER': environ['DB_USER'],
        'PASSWORD': environ['DB_PASSWORD']
    }
}

MONGO_URI = environ.get("MONGO_URI")
MONGO_NAME = environ.get("MONGO_NAME")
MONGO_HOST = environ.get("MONGO_HOST")
MONGO_PORT = int(environ.get("MONGO_PORT", 27017))
MONGO_USER = environ.get("MONGO_USER", None)
MONGO_PASSWORD = environ.get("MONGO_PASSWORD", None)

USE_REDIS = eval(environ.get("USE_REDIS", "True"))
if USE_REDIS:
    REDIS_HOST = environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(environ.get("REDIS_DB", 0))
    REDIS_PASSWORD = None

    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    REDIS_CONN = redis.Redis.from_url(REDIS_URL)

    RQ_QUEUES = {
        q: {
            # 'URL': REDIS_URL, 
            'HOST': REDIS_HOST,
            'PORT': REDIS_PORT,
            'DB': REDIS_DB,
            'PASSWORD': REDIS_PASSWORD,
            'DEFAULT_TIMEOUT': 480
        } for q in JobQ.ALL_QS
    }

CRON_CLASSES = JOB_HANDLER_APP_CRON + MIDDLEWARE_APP_CRON + USER_APP_CRON


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    # prithoo: We WANT this to break if it cannot find the algorithm.
    'ALGORITHM': environ['JWT_ALGORITHM'],
    'SIGNING_KEY': SECRET_KEY,
}

if ENV_TYPE == "dev":
    SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(hours=8)
    SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=15)


## Create directory for logs
LOG_DIR = path.join(BASE_DIR.parent, 'logs/')
if not path.exists(LOG_DIR):
    makedirs(LOG_DIR)
ENV_LOG_FILE = path.join(LOG_DIR, f'{ENV_TYPE}_root.log')
DJANGO_LOG_FILE = path.join(LOG_DIR, 'django.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s|%(asctime)s.%(msecs)d|%(name)s|%(module)s|%(funcName)s:%(lineno)s]    %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'local': {
            'format': '[%(asctime)s|%(name)s|%(module)s|%(funcName)s:%(lineno)s]    %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'local',
        },
        'root_file': {
            'class': 'logging.FileHandler',
            'filename': ENV_LOG_FILE,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        }
    },
    'loggers': {
        'root': {
            'handlers': [
                'console', 
                'root_file'
            ],
            "level": 'INFO'
        },
    },
}

IP_HEADER = "ip"
MAC_HEADER = "mac"

LANGUAGE_CODE = environ.get("LANGUAGE_CODE", "en-us")
TIME_ZONE = environ.get("TIME_ZONE", "utc")
USE_I18N = eval(environ.get("USE_I18N", "True"))
USE_TZ = eval(environ.get("USE_TZ", "True"))

STATIC_URL = '/static/'
STATIC_ROOT = 'static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'user_app.User'
CORS_ORIGIN_WHITELIST = environ.get('CORS_ORIGIN_WHITELIST', '').split(', ')
CORS_ORIGIN_ALLOW_ALL = True

OTP_ATTEMPT_LIMIT = int(environ.get('OTP_ATTEMPT_LIMIT', 10000))
OTP_ATTEMPT_TIMEOUT = int(environ.get('OTP_ATTEMPT_TIMEOUT', 0))

AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = environ.get("AWS_REGION_NAME")
SNS_SENDER_ID = environ.get("SNS_SENDER_ID", "Test-App")