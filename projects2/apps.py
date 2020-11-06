from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = 'projects2'

    def ready(self):
        import projects2.signals