from django.core.management.base import BaseCommand, CommandError
from pages.plugins.pofiles.utils import import_po_files

class Command(BaseCommand):
    args = '<path>'
    help = import_po_files.__doc__

    def handle(self, *args, **options):
        import_po_files(*args)