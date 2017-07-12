"""
WSGI config for bitpoll project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
try:
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    raven_support = True
except ImportError:
    raven_support = False

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitpoll.settings")

if raven_support:
    application = Sentry(get_wsgi_application())
else:
    application = get_wsgi_application()
