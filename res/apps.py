from django.apps import AppConfig


class resConfig(AppConfig):
    name = 'res'

    def ready(self):
        import res.signals
