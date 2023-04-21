from django.apps import AppConfig


class MiddlewareAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'middleware_app'
    verbose_name = "Middlewares"