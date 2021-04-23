from django.apps import AppConfig


class CsasConfig(AppConfig):
    name = 'csas2'

    def ready(self):
        import csas2.signals
