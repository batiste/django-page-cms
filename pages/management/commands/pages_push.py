from django.core.management.base import BaseCommand, CommandError
import requests
import os
import json

class Command(BaseCommand):
    help = 'Pull data from an API'

    def add_arguments(self, parser):
        parser.add_argument('host', type=str)
        parser.add_argument('auth', type=str)
        parser.add_argument('--filename', type=str,  default="data/download.json")

    def handle(self, *args, **options):
        auth = options['auth'].split(':')
        host = options['host']
        filename = options['filename']

        with open(filename, "r") as f:
            data = f.read()
            pages = json.loads(data)
            for page in pages['results']:
                print("Pushing page " + str(page['id']))
                data = json.dumps(page)
                url = host + 'api/' + str(page['id']) + '/'
                headers = {'Content-Type': 'application/json' }
                response = requests.put(url, data=data, auth=(auth[0], auth[1]), headers=headers)
                if response.status_code != 200:
                    raise ValueError(response.status_code, response.text)


