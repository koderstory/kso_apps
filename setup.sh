#!/bin/bash

# Generate passowrds
DBPASS=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c12`
#SFTPPASS=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c12`

# Input domain name
echo -ne "Enter your domain name:"
read DOMAIN

HOMEDIR="$(pwd)/websites/$DOMAIN"
mkdir -p "$HOMEDIR/.venv"
cd $HOMEDIR

# -------------------------------------------------------------
sudo -H pip install -U pipenv

pipenv install django gunicorn django-environ psycopg2 pillow whitenoise djlint
source "$HOMEDIR/.venv/bin/activate"
django-admin startproject config .

# --------------------------------------------------------------
touch $HOMEDIR/.env
echo "
#-- KEY
SECRET_KEY=$DBPASS

#-- DEBUG STATUS
DEBUG=True

#-- HOST
HOSTS=127.0.0.1,0.0.0.0,localhost,$DOMAIN,www.$DOMAIN

#-- POSTGRESQL CONFIG
#DATABASE_URL=psql://yourusername:yourpassword@127.0.0.1:5432/yourdatabase

#-- SQLITE CONFIG
DATABASE_URL=sqlite:///sqlite.db

#-- MEMCACHE CONFIG
# CACHE_URL=memcache://127.0.0.1:11211,127.0.0.1:11212,127.0.0.1:11213

#-- REDIS CONFIG
# REDIS_URL=rediscache://127.0.0.1:6379/1?client_class=django_redis.client.DefaultClient&password=ungithubbed-secret
" | tee $HOMEDIR/.env >> $HOMEDIR/deploy.log

# -------------------------------------------------------------
echo "
from pathlib import Path
import environ
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------
# Environment
# ---------------------
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

# DOMAINS or HOSTS
ALLOWED_HOSTS = env.list('HOSTS')

# ---------------------
# Application definition
# ---------------------
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core.apps.CoreConfig',
    'authentication.apps.AuthenticationConfig',
    'website.apps.WebsiteConfig',
]

# ------------------------
# SSL
# -----------------------
#if DEBUG == False:
#    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#    SECURE_SSL_REDIRECT = False
#    CSRF_TRUSTED_ORIGINS = ['https://'+ALLOWED_HOSTS[0]]
#    CSRF_COOKIE_DOMAIN = ['https://'+ALLOWED_HOSTS[0]]
#    CSRF_COOKIE_SECURE = True


# ---------------------
# MIDDLEWARE
# ---------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # whitenoise
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'config.urls'

# ---------------------
# Templates
# ---------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# ---------------------
DATABASES = {
    'default':env.db()
}

# ---------------------
# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
# ---------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ---------------------
# Assets
# ---------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
#STATICFILES_DIRS = [BASE_DIR / "resources", ]
#STATIC_ROOT = BASE_DIR / 'public/static'
#STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
#MEDIA_ROOT = BASE_DIR / 'public/media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------
# USER
#AUTH_USER_MODEL = 'authentication.Account'
" | tee $HOMEDIR/config/settings.py >> $HOMEDIR/deploy.log

# --------------------------------------------------------------
echo "[Unit]
Description=gunicorn socket -> $DOMAIN

[Socket]
ListenStream=/run/gunicorn_$DOMAIN.sock

[Install]
WantedBy=sockets.target
"| sudo tee /etc/systemd/system/gunicorn_$DOMAIN.socket >> $HOMEDIR/deploy.log

# -----------------------------------------
echo "[Unit]
Description=gunicorn $DOMAIN daemon
Requires=gunicorn_$DOMAIN.socket
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$HOMEDIR
ExecStart=$HOMEDIR/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn_$DOMAIN.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
" | sudo tee /etc/systemd/system/gunicorn_$DOMAIN.service >> $HOMEDIR/deploy.log

# -----------------------------------------------------
sudo systemctl start gunicorn_$DOMAIN.socket
sudo systemctl enable gunicorn_$DOMAIN.socket
curl --unix-socket /run/gunicorn_$DOMAIN.sock localhost >> $HOMEDIR/deploy.log
sudo systemctl daemon-reload

# -------------------------------------------------------------
echo "server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    error_log /var/log/nginx/.$DOMAIN_error.log;
    access_log /var/log/nginx/.$DOMAIN_access.log;
    rewrite_log on;
    server_tokens off;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection '1; mode=block';

    location /static/ {
        root $HOMEDIR;
            expires 30d;
        log_not_found off;
        access_log off;
    }
    location /media/ {
        root $HOMEDIR;
            expires 30d;
        log_not_found off;
        access_log off;
     }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn_$DOMAIN.sock;
    }
}
" | sudo tee /etc/nginx/sites-available/$DOMAIN >> $HOMEDIR/deploy.log
sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled
sudo systemctl restart nginx


# -------------------------------------------------------------
printf "✅✅✅✅✅  INSTALLATION COMPLETE  ✅✅✅✅✅\n\n"



