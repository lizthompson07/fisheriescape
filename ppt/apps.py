from django.apps import AppConfig


class PPTConfig(AppConfig):
    name = 'ppt'

    def ready(self):
        import ppt.signals