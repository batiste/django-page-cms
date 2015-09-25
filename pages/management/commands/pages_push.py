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
                page_id = str(page['id'])
                print("Pushing page " + page_id)
                data = json.dumps(page)
                url = host + 'api/' + page_id + '/'
                headers = {'Content-Type': 'application/json'}
                # try an update first
                response = requests.put(url, data=data, auth=(auth[0], auth[1]), headers=headers)
                if response.status_code == 404:# or response.status_code == 400:
                    print("Page " + page_id + " doesn't exist on the target. Skiped.")
                    continue
                if response.status_code != 200 and response.status_code != 201:
                    raise ValueError(response.status_code, response.text)


