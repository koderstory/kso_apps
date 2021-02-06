#!/bin/bash

NAME="urdomain.com"
DIR=/home/dev/urdomain.com
USER=dev
GROUP=dev
WORKERS=3
BIND=0.0.0.0:8080

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
