from pathlib import Path
from configurations import Configuration
import environ


env = environ.Env()
environ.Env.read_env(env.str('ENV_PATH', '../.env'))
BASE_DIR = Path(__file__).resolve().parent.parent

class Development(Configuration):

    # ---------------------
    # Host
    # ---------------------
    SECRET_KEY = env('SECRET_KEY')
    DEBUG = env('DEBUG')
    SITE_HOST = env.str('SITE_HOST')
    SITE_URL_HTTP = 'http://{}'.format(SITE_HOST)
    SITE_URL_HTTPS = 'https://{}'.format(SITE_HOST)

    if env.bool('USE_SSL', default=False):
        DEFAULT_SITE_URL = SITE_URL_HTTPS
    else:
        DEFAULT_SITE_URL = SITE_URL_HTTP
    ALLOWED_HOSTS = env.list('HOSTS')
    
    # ---------------------
    # Advance config
    # ---------------------
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
        'whitenoise.middleware.WhiteNoiseMiddleware',
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
    DATABASES = {'default': env.db(), }
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
    
    # ---------------------
    # Time and location
    # ---------------------
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # ---------------------
    # Assets
    # ---------------------
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    STATICFILES_DIRS = [
        BASE_DIR / "assets",
    ]
    STATIC_ROOT = BASE_DIR.parent / 'files/static'
    MEDIA_ROOT = BASE_DIR.parent / 'files/media'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # ---------------------
    # Whitenoise
    # ---------------------
    WHITENOISE_INDEX_FILE = True



class Production(Development):
    ALLOWED_HOSTS = env.list('HOSTS')
    DEBUG = env('DEBUG')
