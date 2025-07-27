#!/bin/bash

fd --type f --extension py "000[0-9]_initial.py" -I -x rm {}

source ./purly/backend/.venv/bin/activate

python manage.py makemigrations
python manage.py migrate
python manage.py create_fake_data
