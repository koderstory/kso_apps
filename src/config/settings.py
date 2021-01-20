from pathlib import Path
from configurations import Configuration
import environ


env = environ.Env()
environ.Env.read_env(env.str('ENV_PATH', '../.env'))


class Development(Configuration):

    SITE_HOST = env.str('SITE_HOST')
    SITE_URL_HTTP = 'http://{}'.format(SITE_HOST)
    SITE_URL_HTTPS = 'https://{}'.format(SITE_HOST)

    if env.bool('USE_SSL', default=False):
        DEFAULT_SITE_URL = SITE_URL_HTTPS
    else:
        DEFAULT_SITE_URL = SITE_URL_HTTP

    BASE_DIR = Path(__file__).resolve().parent.parent
    SECRET_KEY = env('SECRET_KEY')
    DEBUG = env('DEBUG')
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
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
    DATABASES = {'default': env.db(),}
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
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    STATIC_URL = '/static/'


class Production(Development):
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
    DEBUG = env('DEBUG')
