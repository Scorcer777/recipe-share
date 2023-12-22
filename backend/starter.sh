#!/bin/sh

while ! nc -z db 5432;
    do sleep .5;
    echo "wait database";
done;
    echo "connected to the database";

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput --first_name Kirill --last_name Novoselov
python manage.py loaddata data/user.json
python manage.py loaddata data/ingredient.json
python manage.py loaddata data/tag.json
gunicorn -w 2 -b 0:8000 foodgram_project.wsgi:application