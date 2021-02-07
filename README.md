# Django 3 project template

This is a simple Django 3.x template project. Ready to deploy to VPS like [Upcloud](https://upcloud.com/signup/?promo=ZR5NUN), Linode, Digital Ocean etc.

## Features

- Django 3.0+
- Uses [Pipenv](https://github.com/kennethreitz/pipenv) - the officially recommended Python packaging tool from Python.org.
- Development,Production settings with [django-configurations](https://django-configurations.readthedocs.org).
- Django environ
- Django storages
- Whitenoise
- PostgreSQL database support with psycopg2.

## How to install

```bash
curl -s -L http://bit.ly/djtemplate -o dt && chmod u+x dt && ./dt
```

![](installation.gif)

## Configuration

By default setting is in production ready mode. In case you need to change or custom it then edit `.env` file,`settings.py` or `.gunicorn.sh.

**.env**
```bash
# ==============
# GLOBAL
# ==============

SECRET_KEY=MYKEY

# True/False --- Dont forget capital
DEBUG=MYDEBUG

# Website
SITE_HOST=MYDOMAIN

# change to your domain + ip
HOSTS=MYDOMAIN         
USE_SSL=True

# ==============
# DATABASE
# ==============

# DB - Postgresql
# DATABASE_URL=psql://username:password@127.0.0.1:5432/django101

DATABASE_URL=sqlite:///sqlite.db

# CACHE_URL=memcache://127.0.0.1:11211,127.0.0.1:11212,127.0.0.1:11213
# REDIS_URL=rediscache://127.0.0.1:6379/1?client_class=django_redis.client.DefaultClient&password=ungithubbed-secret

# ==============
# ASSETS
# ==============

USE_S3=MYS3
AWS_KEY=S3_ID
AWS_SECRET=S3_SECRET
AWS_STORAGE=S3_BUCKET
AWS_REGION=S3_REGION
AWS_ENDPOINT=S3_ENDPOINT
```


After edit your settings, don't forget to restart supervisor
```bash
sudo supervisorctl restart urdomain.com
```
