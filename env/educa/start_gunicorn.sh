#!/bin/bash
cd /home/aymen/PycharmProjects/myapp/educa
source /home/aymen/PycharmProjects/myapp/env/educa/bin/activate
exec gunicorn --access-logfile - --workers 3 --bind unix:/home/aymen/PycharmProjects/myapp/educa/educa.sock educa.wsgi:application
