from django.db import models
from django.contrib.auth.models import AbstractUser


USER_LANG = (
    ('german', 'German'),
    ('english', 'English'),
)


class DudelUser(AbstractUser):
    language = models.CharField(max_length=20, choices=USER_LANG, default="english")
    email_invitation = models.BooleanField(default=True)
    timezone = models.CharField(max_length=40, default="Europe/Berlin")
    auto_watch = models.BooleanField(default=False)
