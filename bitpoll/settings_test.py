"""Django settings used by the pytest suite.

The regular settings remain the source of truth; this module only disables
production-only static manifest behavior and external integrations.
"""

from .settings import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

