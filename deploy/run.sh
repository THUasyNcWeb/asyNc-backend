#!/bin/sh
python manage.py migrate
gunicorn -b 0.0.0.0:80 --access-logfile - --log-level info asyNc.wsgi
