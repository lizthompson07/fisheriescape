from django.apps import AppConfig


class MasterlistConfig(AppConfig):
    name = 'masterlist'

    def ready(self):
        import masterlist.signals