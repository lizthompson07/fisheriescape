from django.apps import AppConfig


class SharedModelsConfig(AppConfig):
    name = 'shared_models'

    def ready(self):
        import shared_models.signals
