#!/bin/bash
set -e
export DJANGO_SETTINGS_MODULE=Project.settings
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput
