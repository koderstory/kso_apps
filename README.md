# Django 3 project template

This is a simple Django 3.0+ project. 

## Features

- Django 3.0+
- Uses [Pipenv](https://github.com/kennethreitz/pipenv) - the officially recommended Python packaging tool from Python.org.
- Development,Production settings with [django-configurations](https://django-configurations.readthedocs.org).
- PostgreSQL database support with psycopg2.

## How to install

```bash
django-admin startproject \
    --template=https://github.com/koderstory/djangotemplate/raw/main/djangotemplate.zip \
    ProjectName
cd ProjectName
pipenv install --dev
```
