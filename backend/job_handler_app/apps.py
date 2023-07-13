from django.apps import AppConfig


class JobHandlerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_handler_app'
    verbose_name = 'Job Handler Application'

    def ready(self):
        import job_handler_app.signals
