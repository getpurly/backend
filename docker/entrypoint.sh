#!/bin/sh

# Wait for database if necessary
sleep 10

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_initial_superuser

unset DJANGO_SUPERUSER_USERNAME
unset DJANGO_SUPERUSER_EMAIL
unset DJANGO_SUPERUSER_PASSWORD

exec gunicorn config.wsgi.application --workers 2 --timeout 60 --bind 0.0.0.0:8000
