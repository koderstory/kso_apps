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
curl -s -L https://bit.ly/36RMnfH -o dt && chmod u+x dt && ./dt
```

## Configuration

By default setting is is production ready. In case you need to edit, edit file `.env` in your folder project or if you need to edit your `settings.py` `or .gunicorn.sh` to change running development mode if running in local server/ your computer.

**.env**
```dotenv
SECRET_KEY=123

# True/False --- Dont forget capital
DEBUG= False

# Website
SITE_HOST= <your main domain>

# change to your domain + ip
HOSTS=urdomain.com, www.urdomain.com        
USE_SSL=True

# DB - Postgresql
# DATABASE_URL=psql://username:password@127.0.0.1:5432/django101

DATABASE_URL=sqlite:///../sqlite.db

# CACHE_URL=memcache://127.0.0.1:11211,127.0.0.1:11212,127.0.0.1:11213
# REDIS_URL=rediscache://127.0.0.1:6379/1?client_class=django_redis.client.DefaultClient&password=ungithubbed-secret
```


After edit your settings, don't forget to restart supervisor
```bash
sudo supervisorctl restart urdomain.com
```
