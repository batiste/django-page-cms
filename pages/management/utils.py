from django.core.management.base import BaseCommand, CommandError
import requests
import os
import sys

class APICommand(BaseCommand):
    help = 'Base API command'

    def parse_options(self, options):
        auth = options['auth'].split(':')
        self.auth = (auth[0], auth[1])
        self.verbosity = options.get('verbosity', 1)
        host = options['host']
        if not host.endswith('/'):
            host = host + '/'
        if not host.startswith('http://'):
            host = 'http://' + host
        self.host = host
        self.filename = options['filename']

    def http_error(self, response):
        with open('error.html', "w") as f:
            f.write(response.text)
        raise ValueError("Error type " + str(response.status_code) + " file written: error.html")

    def cprint(self, msg):
        if self.verbosity > 0:
            print(msg)

    def cout(self, msg):
        if self.verbosity > 0:
            sys.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument('auth', type=str,
            help='authentication in the form user:password')
        parser.add_argument('--host', type=str,
            help='server to pull from', 
            default='http://127.0.0.1:8000/api/')
        parser.add_argument('--filename', type=str,
            default="data/download.json")