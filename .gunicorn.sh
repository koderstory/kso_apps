#!/bin/bash
DEBUG_MODE=$(egrep -w DEBUG .env)
cd src
if [ "$DEBUG_MODE" = "DEBUG=True" ]; then
        pipenv run gunicorn --env DJANGO_SETTINGS_MODULE=config.settings --env DJANGO_CONFIGURATION=Development  config.wsgi -b 0.0.0.0:8000
else
        pipenv run gunicorn --env DJANGO_SETTINGS_MODULE=config.settings --env DJANGO_CONFIGURATION=Production  config.wsgi -b 0.0.0.0:8000
fi

