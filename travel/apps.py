from django.apps import AppConfig


class TravelConfig(AppConfig):
    name = 'travel'

    def ready(self):
        import travel.signals