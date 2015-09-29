from django.core.management.base import BaseCommand, CommandError
import requests
import os

class Command(BaseCommand):
    help = 'Pull data from a Django Page CMS API'

    def add_arguments(self, parser):
        parser.add_argument('auth', type=str,
            help='authentication in the form user:password')
        parser.add_argument('--host', type=str,
            help='server to pull from', 
            default='http://127.0.0.1:8000/api/')
        parser.add_argument('--filename', type=str,
            default="data/download.json")

    def handle(self, *args, **options):
        auth = options['auth'].split(':')
        host = options['host']
        if not host.endswith('/'):
            host = host + '/'

        print("Fetching page data on " + host)
        host = host + '?format=json'
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
