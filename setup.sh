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

# --------------------------------------------------------------
echo "
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------
# Environment
# ---------------------
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('HOSTS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"| tee $HOMEDIR/config/settings.py >> $HOMEDIR/deploy.log

# --------------------------------------------------------------
echo "[Unit]
Description=gunicorn socket -> $DOMAIN

[Socket]
ListenStream=/run/gunicorn_$DOMAIN.sock

[Install]
WantedBy=sockets.target
"| sudo tee /etc/systemd/system/gunicorn_$DOMAIN.socket >> $HOMEDIR/deploy.log

# -----------------------------------------
sudo rm -r /etc/systemd/system/gunicorn_$DOMAIN.service >> /dev/null
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
sudo rm -f /etc/nginx/sites-available/$DOMAIN >> /dev/null
sudo rm -f /etc/nginx/sites-enabled/$DOMAIN >> /dev/null
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



