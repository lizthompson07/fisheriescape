from django.apps import AppConfig


class TrapnetConfig(AppConfig):
    name = 'trapnet'

    def ready(self):
        import trapnet.signals
