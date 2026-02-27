#!/usr/bin/env python
import os, sys
current_dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dirname, '..'))
sys.path.insert(0, os.path.join(current_dirname, '../..'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
