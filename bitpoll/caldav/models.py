from django.db import models

from bitpoll.base.models import BitpollUser


class DavCalendar(models.Model):
    user = models.ForeignKey(BitpollUser, on_delete=models.CASCADE)
    url = models.URLField()
