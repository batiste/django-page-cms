from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BasicCmsConfig(AppConfig):
    name = 'pages'
    verbose_name = _("Pages")

    def ready(self):
        from . import checks
