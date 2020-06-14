from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from bitpoll.base.validators import validate_timezone

USER_LANG = (
    ('german', 'German'),
    ('english', 'English'),
)


class BitpollUser(AbstractUser):
    language = models.CharField(max_length=20, choices=USER_LANG, default="english")
    email_invitation = models.BooleanField(default=True, verbose_name=_('Email Invitations'), help_text=_('Send E-Mails if you are invited to a poll or group'))
    timezone = models.CharField(max_length=40, default=settings.TIME_ZONE, validators=[validate_timezone])
    auto_watch = models.BooleanField(default=False, help_text=_('Automatically watch polls you have voted in'), verbose_name=_('Auto Watch Polls'))
    displayname = models.CharField(max_length=20, default="")

    def get_displayname(self):
        if self.displayname:
            return self.displayname
        else:
            return self.get_short_name() + ' (' + self.username + ')'
