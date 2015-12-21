from django.core.management.base import BaseCommand, CommandError
import requests
import os
import json
import sys
from pages.management.utils import APICommand

class Command(APICommand):
    help = 'Push data to a Django Page CMS API'

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
                self.http_error(response)
            self.cout('.')

    def push_page(self, page):
        page_id = str(page['id'])
        auth = self.auth

        headers = {'Content-Type': 'application/json'}

        server_page = self.uuid_mapping.get(page['uuid'], None)

        # we don't change the parent if for a reason or another it is
        # not present on the server
        if self.server_id_mapping.get(page['parent']):
            page['parent'] = self.server_id_mapping[page['parent']]
        else:
            del page['parent']

        if server_page:
            self.server_id_mapping[page['id']] = server_page['id']
            page['id'] = server_page['id']
            self.cout("Update page " + str(page['id']))
            url = self.host + 'pages/' + str(page['id']) + '/'
            data = json.dumps(page)
            response = requests.put(url, data=data, auth=self.auth, headers=headers)
        else:
            self.cout("Create page " + str(page['id']))
            url = self.host
            data = json.dumps(page)
            response = requests.post(url, data=data, auth=self.auth, headers=headers)
            if response.status_code == 201:
                new_page = json.loads(response.text)
                new_page['content_set'] = page['content_set']
                self.server_id_mapping[page['id']] = new_page['id']
                self.uuid_mapping[new_page['uuid']] = new_page
                page = new_page

        if response.status_code != 200 and response.status_code != 201:
            self.http_error(response)

        self.cout(' .')
        self.push_content(page)

        self.cprint('')

    def handle(self, *args, **options):
        self.parse_options(options)

        self.uuid_mapping = {}
        self.server_id_mapping = {}

        self.cprint("Fetching the state of the pages on the server " + self.host)
        host = self.host + '?format=json'
        response = requests.get(host, auth=self.auth)
        if response.status_code != 200:
            self.http_error(response)
        self.current_page_list = json.loads(response.text)
        
        for page in self.current_page_list:
            self.uuid_mapping[page['uuid']] = page

        with open(self.filename, "r") as f:
            data = f.read()
            pages = json.loads(data)
            for page in pages:
                self.push_page(page)

