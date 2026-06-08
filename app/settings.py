"""
Django settings for app project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ('1', 'true', 'yes', 'on')


def require_env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise ImproperlyConfigured('%s must be set in the environment.' % name)
    return value


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
DEBUG = env_bool('DJANGO_DEBUG', False)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-rest-apis-local-development-key'
    else:
        raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is disabled.')

# SECURITY WARNING: don't run with debug turned on in production!
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'south',
    'app',
    'home'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
)

ROOT_URLCONF = 'app.urls'

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Get your Twitter key/secret from https://apps.twitter.com/
SOCIAL_AUTH_TWITTER_KEY = require_env('SOCIAL_AUTH_TWITTER_KEY', '')
SOCIAL_AUTH_TWITTER_SECRET = require_env('SOCIAL_AUTH_TWITTER_SECRET', '')

TWITTER_ACCESS_TOKEN = require_env('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = require_env('TWITTER_ACCESS_TOKEN_SECRET', '')

SOCIAL_AUTH_LOGIN_URL          = '/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/home'
SOCIAL_AUTH_LOGIN_ERROR_URL    = '/login-error/'

LOGIN_URL = '/login/twitter'
