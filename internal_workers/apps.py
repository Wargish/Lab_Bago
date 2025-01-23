from django.apps import AppConfig


class InternalWorkersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'internal_workers'

    def ready(self):
        from internal_workers import signals
