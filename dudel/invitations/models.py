from django.db import models
from django.contrib.auth.models import User  # Group

from dudel.poll.models import Poll, Vote


class Invitation(models.Model):
    date_created = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)

    def __str__(self):
        return u'Invitation {}'.format(self.id)
