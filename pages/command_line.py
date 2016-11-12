#!/usr/bin/env python
import argparse
import os
import shutil
import stat
from subprocess import call
from six.moves import input
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_DIR = os.path.join(PROJECT_DIR, 'example')

parser = argparse.ArgumentParser(description='Gerbi CMS console tool.')
parser.add_argument('--create', type=str,
                    help='Create a new CMS example website')


def print_green(msg):
    print('\033[92m' + msg + '\033[0m')


def main():
    args = parser.parse_args()

    if args.create:
        absolute = os.path.join(os.getcwd(), args.create)
        print_green("Creating website {}".format(args.create))
        print_green("Copying example files to {}".format(args.create))
        ignore = shutil.ignore_patterns('*.db', '*.pyc', 'media', 'whoosh*')
        shutil.copytree(EXAMPLE_DIR, args.create, ignore=ignore)
        st = os.stat(os.path.join(args.create, 'manage.py'))
        os.chmod(os.path.join(args.create, 'manage.py'), st.st_mode | stat.S_IEXEC)
        ret = call(['./manage.py'.format(args.create), 'migrate'], cwd=absolute)
        if ret != 0:
            return
        print_green('Migration done')
        _input = input("Would you like to create a superuser to connect to the admin? [N/y] ")
        if _input.lower() == 'y':
            call(['./manage.py'.format(args.create), 'createsuperuser'], cwd=absolute)
        print_green('Creating demo pages')
        call(['./manage.py'.format(args.create), 'pages_demo'], cwd=absolute)
        print_green('Rebuild search index')
        call(['./manage.py'.format(args.create), 'rebuild_index', '--noinput'], cwd=absolute)
        print_green('Run webserver')
        call(['./manage.py'.format(args.create), 'runserver'], cwd=absolute)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()