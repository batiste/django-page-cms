from django.core.management.base import BaseCommand, CommandError
from django_gerbi.utils import export_po_files

class Command(BaseCommand):
    args = '<path>'
    help = export_po_files.__doc__

    def handle(self, *args, **options):
        export_po_files(*args)