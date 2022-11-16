from django.apps import AppConfig


class HerringConfig(AppConfig):
    name = 'herring'

    def ready(self):
        import herring.signals
