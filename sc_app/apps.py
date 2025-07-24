from django.apps import AppConfig


class ScAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sc_app'

    def ready(self):
        import sc_app.models  # Ensures Django loads models/__init__.py
