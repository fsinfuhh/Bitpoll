from django.db import models
from encrypted_model_fields.fields import EncryptedMixin

from bitpoll.base.models import BitpollUser


class EncryptedURLField(EncryptedMixin, models.URLField):
    pass


class DavCalendar(models.Model):
    user = models.ForeignKey(BitpollUser, on_delete=models.CASCADE)
    url = EncryptedURLField()
    name = models.CharField(max_length=80)
