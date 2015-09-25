from django.core.management.base import BaseCommand, CommandError
import requests
import os

class Command(BaseCommand):
    help = 'Pull data from an API'

    def add_arguments(self, parser):
        parser.add_argument('host', type=str)
        parser.add_argument('auth', type=str)
        parser.add_argument('--filename', type=str,  default="data/download.json")

    def handle(self, *args, **options):
        auth = options['auth'].split(':')
        host = options['host'] + 'api/?format=json'
        filename = options['filename']

        page_list = requests.get(host, auth=(auth[0], auth[1]))
        if page_list.status_code != 200:
            raise ValueError(page_list.status_code)
        json = page_list.text
        
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w") as f:
            f.write(json)
        print(filename + " written to disk")
