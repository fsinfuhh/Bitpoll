# Settings file for Docker Build
import os

SECRET_KEY = '...'

# generate via: ./manage.py generate_encryption_key
FIELD_ENCRYPTION_KEY = "BnEAJ5eEXb4HfYbaCPuW5RKQSoO02Uhz1RH93eQz0GM="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

PIPELINE_LOCAL = {}
PIPELINE_LOCAL['JS_COMPRESSOR'] = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'
PIPELINE_LOCAL['CSS_COMPRESSOR'] = 'pipeline.compressors.cssmin.CSSMinCompressor'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
## https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CSP_ADDITIONAL_SCRIPT_SRC = ['sentry.mafiasi.de']
INSTALLED_APPS_LOCAL = []