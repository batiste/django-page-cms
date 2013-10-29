from django.utils.translation import ugettext as _
from django.core.management.base import BaseCommand, CommandError
from pages.plugins.jsonexport.utils import (pages_to_json,
    monkeypatch_remove_pages_site_restrictions)
from pages.models import Page

from optparse import make_option
import sys

class Command(BaseCommand):
    args = '<site>'
    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all_sites',
            default=False,
            help="export all sites from the database",
        ),)

    def handle(self, site=None, **options):
        """
        Export pages in JSON format.  Site may be specified by id or domain.
        Default: export pages from the current site specified by settings.SITE_ID.
        """
        if options['all_sites']:
            monkeypatch_remove_pages_site_restrictions()
        qs = Page.objects.all()
        if site:
            for match in ('pk', 'domain'):
                try:
                    s = Site.objects.get(**{match:site})
                    break
                except (Site.objects.DoesNotExist, ValueError):
                    continue
            else:
                raise CommandError(_("Site with id/domain = '%s' not found")
                    % site)
            qs.filter(site=s)

        sys.stdout.write(pages_to_json(qs))

