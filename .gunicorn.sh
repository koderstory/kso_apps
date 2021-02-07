#!/bin/bash

NAME=MYDOMAIN
DIR=MYDIR
USER=MYUSER
GROUP=MYUSER
WORKERS=3
BIND=MYBIND

cd $DIR
source .venv/bin/activate
cd src


exec ../.venv/bin/gunicorn config.wsgi \
        --env DJANGO_SETTINGS_MODULE=config.settings \
        --env DJANGO_CONFIGURATION=Development \
        --bind $BIND \
        --workers $WORKERS \
        --name $NAME \
        --group $GROUP
