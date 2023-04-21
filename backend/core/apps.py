DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken'
]

CUSTOM_APPS = [
    'communications_app.apps.CommunicationsAppConfig',
    'middleware_app.apps.MiddlewareAppConfig',
    'user_app.apps.UserAppConfig'
]