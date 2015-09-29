from django.core.management.base import BaseCommand, CommandError
import requests
import os
import json
import sys

def http_error(response):
    with open('error.html', "w") as f:
        f.write(response.text)
    raise ValueError("Error type " + str(response.status_code) + " file written: error.html")

class Command(BaseCommand):
    help = 'Push data to a Django Page CMS API'

    def add_arguments(self, parser):
        parser.add_argument('auth', type=str,
            help='authentication in the form user:password')
        parser.add_argument('--host', type=str,
            help='server to pull from', 
            default='http://127.0.0.1:8000/api/')
        parser.add_argument('--filename', type=str,
            default="data/download.json")

    def push_content(self, page):
        page_id = str(page['id'])
        auth = self.auth
        headers = {'Content-Type': 'application/json'}
        for content in page['content_set']:
            content['page'] = page_id
            data = json.dumps(content)
            url = self.host + 'contents/' + str(content['id']) + '/'
            response = requests.put(url, data=data, auth=self.auth, headers=headers)
            if response.status_code == 404:
                url = self.host + 'contents/'
                response = requests.post(url, data=data, auth=self.auth, headers=headers)
            if response.status_code != 200 and response.status_code != 201:
                http_error(response)
            sys.stdout.write('.')

    def push_page(self, page):
        page_id = str(page['id'])
        auth = self.auth

        headers = {'Content-Type': 'application/json'}

        server_page = self.datetime_mapping.get(page['creation_date'], None)

        # we don't change the parent if for a reason or another it is
        # not present on the server
        if self.server_id_mapping.get(page['parent']):
            page['parent'] = self.server_id_mapping[page['parent']]
        else:
            del page['parent']

        if server_page:
            self.server_id_mapping[page['id']] = server_page['id']
            page['id'] = server_page['id']
            sys.stdout.write("Update page " + str(page['id']))
            url = self.host + 'pages/' + str(page['id']) + '/'
            data = json.dumps(page)
            response = requests.put(url, data=data, auth=self.auth, headers=headers)
        else:
            sys.stdout.write("Create page " + str(page['id']))
            url = self.host
            data = json.dumps(page)
            response = requests.post(url, data=data, auth=self.auth, headers=headers)
            if response.status_code == 201:
                new_page = json.loads(response.text)
                new_page['content_set'] = page['content_set']
                self.server_id_mapping[page['id']] = new_page['id']
                self.datetime_mapping[new_page['creation_date']] = new_page
                self.id_mapping[new_page['id']] = new_page
                page = new_page

        if response.status_code != 200 and response.status_code != 201:
            http_error(response)

        sys.stdout.write(' .')
        self.push_content(page)

        print('')

    def handle(self, *args, **options):
        auth = options['auth'].split(':')
        self.auth = (auth[0], auth[1])
        host = options['host']
        if not host.endswith('/'):
            host = host + '/'
        self.host = host
        filename = options['filename']
        self.datetime_mapping = {}
        self.id_mapping = {}
        self.server_id_mapping = {}

        print("Fetching the state of the pages on the server " + self.host)
        host = self.host + '?format=json'
        response = requests.get(host, auth=self.auth)
        if response.status_code != 200:
            http_error(response)
        self.current_page_list = json.loads(response.text)['results']
        
        for page in self.current_page_list:
            self.datetime_mapping[page['creation_date']] = page
            self.id_mapping[page['id']] = page

        with open(filename, "r") as f:
            data = f.read()
            pages = json.loads(data)
            for page in pages['results']:
                self.push_page(page)

