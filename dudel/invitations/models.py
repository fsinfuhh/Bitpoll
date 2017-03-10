from django.db import models

from dudel.base.models import DudelUser
from dudel.poll.models import Poll, Vote

from datetime import datetime


class Invitation(models.Model):
    class Meta:
        unique_together = ('user', 'poll')

    date_created = models.DateTimeField()
    creator = models.ForeignKey(DudelUser, on_delete=models.CASCADE, related_name='creator')
    user = models.ForeignKey(DudelUser, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, null=True, blank=True)
    last_invited = models.DateTimeField()

    def send(self):
        # TODO implement
        self.last_invited = datetime.now()

    def __str__(self):
        return u'Invitation {}'.format(self.id)
