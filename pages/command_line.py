#!/usr/bin/env python
import argparse
import os
import shutil
import stat
from subprocess import call
import fileinput
import random
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_DIR = os.path.join(PROJECT_DIR, 'example')

parser = argparse.ArgumentParser(description='Gerbi CMS console tool.')
parser.add_argument('--create', type=str,
                    help='Create a new CMS example website')


def print_green(msg):
    print('\033[92m' + msg + '\033[0m')
            
def secret_key():
  return ''.join(
    [random.SystemRandom().choice(
      'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)]
  )

def new_secret_key_settings(filename):
  for line in fileinput.input(filename, inplace=True, backup='.bak'):
      if line.startswith('SECRET_KEY ='):
          print("SECRET_KEY = '{}'".format(secret_key()))
      else:
          print(line, end='')
  os.remove(filename + '.bak')

def main():
    args = parser.parse_args()

    if args.create:
        dirname = args.create
        absolute = os.path.join(os.getcwd(), dirname)
        print_green("Creating website {}".format(dirname))
        print_green("Copying example files to {}".format(dirname))
        ignore = shutil.ignore_patterns('*.db', '*.pyc', 'media', 'whoosh*')
        shutil.copytree(EXAMPLE_DIR, dirname, ignore=ignore)
        st = os.stat(os.path.join(dirname, 'manage.py'))
        os.chmod(os.path.join(dirname, 'manage.py'), st.st_mode | stat.S_IEXEC)
        new_secret_key_settings(os.path.join(absolute, 'settings.py'))
        ret = call(['./manage.py', 'migrate'], cwd=absolute)
        if ret != 0:
            return
        print_green('Migration done')
        _input = input("Would you like to create a superuser to connect to the admin? [N/y] ")
        if _input.lower() == 'y':
            call(['./manage.py', 'createsuperuser'], cwd=absolute)
        print_green('Creating demo pages')
        call(['./manage.py', 'pages_demo'], cwd=absolute)
        print_green('Rebuild search index')
        call(['./manage.py', 'rebuild_index', '--noinput'], cwd=absolute)
        print_green('Run webserver')
        call(['./manage.py', 'runserver'], cwd=absolute)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()