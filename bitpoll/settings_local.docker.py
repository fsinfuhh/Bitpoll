import os
import json

ENV_PREFIX = 'BITPOLL'

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# customize to your needs

# You must insert your own random value here
# SECURITY WARNING: keep the secret key used in production secret!
# see <https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#secret-key>
SECRET_KEY = os.environ.get(f'{ENV_PREFIX}_SECRET_KEY', 'not-very-secret')

# generate via: ./manage.py generate_encryption_key
FIELD_ENCRYPTION_KEY = os.environ.get(f'{ENV_PREFIX}_FIELD_ENCRYPTION_KEY', 'this+is+an+example+key+please+generate+one+=')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get(f'{ENV_PREFIX}_DEBUG', 'false').lower() == 'true'

## If Bitpoll is served via HTTPS enable the next two options
SESSION_COOKIE_SECURE = os.environ.get(f'{ENV_PREFIX}_SESSION_COOKIE_SECURE', 'false').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get(f'{ENV_PREFIX}_CSRF_COOKIE_SECURE', 'false').lower() == 'true'

# The root dir bitpoll appears to be in from the web, as configured in the webserver
URL_PREFIX = os.environ.get(f'{ENV_PREFIX}_URL_PREFIX', '')

# Specify which hosts are allowed to access the application
ALLOWED_HOSTS = os.environ.get(f'{ENV_PREFIX}_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS_LOCAL = []

PIPELINE_LOCAL = {}

if os.environ.get(f'{ENV_PREFIX}_COMPRESS_JS', 'false').lower() == 'true':
    PIPELINE_LOCAL['JS_COMPRESSOR'] = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'
if os.environ.get(f'{ENV_PREFIX}_COMPRESS_CSS', 'false').lower() == 'true':
    PIPELINE_LOCAL['CSS_COMPRESSOR'] = 'pipeline.compressors.cssmin.CSSMinCompressor'
if len(PIPELINE_LOCAL) > 0:
    PIPELINE_ENABLED = True


LANGUAGE_CODE = os.environ.get(f'{ENV_PREFIX}_LANGUAGE_CODE', 'en-US')
TIME_ZONE = os.environ.get(f'{ENV_PREFIX}_TIME_ZONE', 'Europe/Berlin')

# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': os.path.join(ROOT_DIR, '_data', 'db.sqlite3'),
   }
}

SITE_NAME = os.environ.get(f'{ENV_PREFIX}_SITE_NAME', 'Bitpoll')
BASE_URL = os.environ.get(f'{ENV_PREFIX}_BASE_URL', 'https://bitpoll.mafiasi.de')

## Url to the Base Homepage and Text on the Link, leave empty to not use this option
HOME_URL = os.environ.get(f'{ENV_PREFIX}_HOME_URL', '')
HOME_URL_NAME = os.environ.get(f'{ENV_PREFIX}_HOME_URL_NAME', '')

## if the imprint URL is not empty use it as an link to the imprint, else use IMPRINT_TEXT
IMPRINT_URL = os.environ.get(f'{ENV_PREFIX}_IMPRINT_URL', '')
IMPRINT_TEXT = os.environ.get(f'{ENV_PREFIX}_IMPRINT_TEXT', '')

REGISTER_ENABLED = os.environ.get(f'{ENV_PREFIX}_REGISTER_ENABLED', 'true').lower() == 'true'
GROUP_MANAGEMENT = REGISTER_ENABLED

if os.environ.get(f'{ENV_PREFIX}_ENABLE_LDAP', 'false').lower() == 'true':
    import ldap
    from django_auth_ldap.config import LDAPSearch

    AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

    AUTH_LDAP_SERVER_URI = os.environ.get(f'{ENV_PREFIX}_AUTH_LDAP_SERVER_URI', 'ldap_host')
    AUTH_LDAP_BIND_DN = os.environ.get(f'{ENV_PREFIX}_AUTH_LDAP_BIND_DN', 'ldap_bind_dn')
    AUTH_LDAP_BIND_PASSWORD = os.environ.get(f'{ENV_PREFIX}_AUTH_LDAP_BIND_PASSWORD', 'ldap_bind_pw')

    AUTH_LDAP_USER_SEARCH_BASE = os.environ.get(f'{ENV_PREFIX}_AUTH_LDAP_USER_SEARCH_BASE', 'ou=People,dc=mafiasi,dc=de')
    AUTH_LDAP_USER_SEARCH_FILTER = os.environ.get(f'{ENV_PREFIX}_AUTH_LDAP_USER_SEARCH_FILTER', '(uid=%(user)s)')
    AUTH_LDAP_USER_SEARCH = LDAPSearch(AUTH_LDAP_USER_SEARCH_BASE, ldap.SCOPE_SUBTREE, AUTH_LDAP_USER_SEARCH_FILTER)
    AUTH_LDAP_ALWAYS_UPDATE_USER = True

    from django_auth_ldap.config import LDAPSearch, PosixGroupType

    AUTH_LDAP_GROUP_SEARCH_BASE = os.environ.get(f'{ENV_PREFIX}_AUTH_LDAP_GROUP_SEARCH_BASE', 'ou=groups,dc=mafiasi,dc=de')
    AUTH_LDAP_GROUP_SEARCH_FILTER = os.environ.get(f'{ENV_PREFIX}_AUTH_LDAP_GROUP_SEARCH_FILTER', '(objectClass=posixGroup)')
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(AUTH_LDAP_GROUP_SEARCH_BASE, ldap.SCOPE_SUBTREE, AUTH_LDAP_GROUP_SEARCH_FILTER)
    AUTH_LDAP_GROUP_TYPE = PosixGroupType()
    #AUTH_LDAP_FIND_GROUP_PERMS = True
    AUTH_LDAP_MIRROR_GROUPS = True

    AUTH_LDAP_USER_ATTR_MAP = json.loads(
        os.environ.get(
            f'{ENV_PREFIX}_AUTH_LDAP_USER_ATTR_MAP',
            '{"first_name": "givenName", "last_name": "sn", "email": "mail"}'
        )
    )
