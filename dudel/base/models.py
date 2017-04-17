from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

from dudel.base.validators import validate_timezone

USER_LANG = (
    ('german', 'German'),
    ('english', 'English'),
)


class DudelUser(AbstractUser):
    language = models.CharField(max_length=20, choices=USER_LANG, default="english")
    email_invitation = models.BooleanField(default=True)
    timezone = models.CharField(max_length=40, default=settings.TIME_ZONE, validators=[validate_timezone])
    auto_watch = models.BooleanField(default=False)
