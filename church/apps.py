from django.apps import AppConfig

class ChurchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'church'

    def ready(self):
        import church.signals  # This ensures your signals are registered
