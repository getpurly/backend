#!/bin/bash

fd --type f --extension py "000[0-9]_initial.py" -I -x rm {}

source ./purly/backend/.venv/bin/activate

export DJANGO_SUPERUSER_USERNAME="dev"
export DJANGO_SUPERUSER_PASSWORD="dev"
export DJANGO_SUPERUSER_EMAIL="dev@localhost"

python manage.py makemigrations
python manage.py migrate
python manage.py create_fake_data
python manage.py createsuperuser --noinput
