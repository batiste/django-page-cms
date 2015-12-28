from django.apps import AppConfig


class BasicCmsConfig(AppConfig):
    name = 'page_cms'

    def ready(self):
        from . import checks
