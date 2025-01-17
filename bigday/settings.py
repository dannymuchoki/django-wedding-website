"""
Django settings for bigday project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import environ

# For Heroku
import django_heroku

# Keep sensitive settings in environ. Also, keep things that are not relevant to other people.  
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'


STATICFILES_DIRS = (
    os.path.join('bigday', 'static'),
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# DO NOT ENTER THE SECRET KEY HERE 
SECRET_KEY = os.getenv('SECRET_KEY', 'Optional default value')

# SECURITY WARNING: don't run with debug turned on in production! You can keep it set to True in your local_settings.py
DEBUG = False

#List variables in the .env file
ENV_HOST_LIST = os.getenv("ALLOWED_HOSTS")
WEDDING_WEBSITE_URL_LIST = os.getenv("WEDDING_WEBSITE_URL")

ALLOWED_HOSTS = ENV_HOST_LIST.split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'guests.apps.GuestsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # whitenoise is necessary for Heroku deployment.
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'bigday.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join('bigday', 'templates'),
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

WSGI_APPLICATION = 'bigday.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
#STATIC_ROOT = 'static_root'
#STATIC_URL = '/static/'


# These are all the environment variables you will need to set in you .env both locally and in the cloud. 
BRIDE_AND_GROOM = os.getenv('BRIDE_AND_GROOM')
# base address for all emails.
DEFAULT_WEDDING_EMAIL = os.getenv('EMAIL_HOST_USER')
# the address your emails (save the dates/invites/etc.) will come from
DEFAULT_WEDDING_FROM_EMAIL = BRIDE_AND_GROOM + ' <' + DEFAULT_WEDDING_EMAIL + '>' # change to 'address@domain.tld'
# the default reply-to of your emails
DEFAULT_WEDDING_REPLY_EMAIL = DEFAULT_WEDDING_EMAIL # change to 'address@domain.tld'
# the all-important Honeymoon Fund
HONEYMOON_FUND = os.getenv('HONEYMOON_FUND')
# the location of your wedding
WEDDING_LOCATION = os.getenv('WEDDING_LOCATION')
# the date of your wedding
WEDDING_DATE = os.getenv('WEDDING_DATE')
# Address of the place of ceremony
CEREMONY_ADDRESS = os.getenv('CEREMONY_ADDRESS')
# Ceremony start time
CEREMONY_START = os.getenv('CEREMONY_START')
# Ceremony Location Google Map
CEREMONY_MAP = os.getenv('OSTERTAG_GOOGLE_MAP')
#Caboose Farm is where the bridal and groom parties stayed. It is 
CABOOSE_FARM_NAME = os.getenv('CABOOSE_FARM_NAME')
# Google Maps URL
CABOOSE_FARM_MAP = os.getenv('CABOOSE_FARM_MAP')
CABOOSE_FARM_ADDRESS = os.getenv('CABOOSE_FARM_ADDRESS')

# when sending test emails it will use this address
DEFAULT_WEDDING_TEST_EMAIL = DEFAULT_WEDDING_FROM_EMAIL

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

# This is used in links in save the date / invitations
WEDDING_WEBSITE_URL = WEDDING_WEBSITE_URL_LIST.split(',') 
WEDDING_CC_LIST = []  # put email addresses here if you want to cc someone on all your invitations


# Added to fix a deprecation error
DEFAULT_AUTO_FIELD='django.db.models.AutoField' 

try:
    from .local_settings import *
except ImportError:
    pass

# For Heroku
django_heroku.settings(locals())