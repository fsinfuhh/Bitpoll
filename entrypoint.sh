#!/bin/sh

./manage.py compilemessages
./manage.py collectstatic
./manage.py migrate
./manage.py runserver 0.0.0.0:8000