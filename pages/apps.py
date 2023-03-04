from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BasicCmsConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'pages'
    verbose_name = _("Pages")

    def ready(self):
        from . import checks
