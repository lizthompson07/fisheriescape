from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    name = 'inventory'

    def ready(self):
        import inventory.signals