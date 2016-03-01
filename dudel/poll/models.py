from django.db import models
from django.contrib.auth.models import Group, User

# Create your models here.

POLL_TYPES = (
    ('universal', 'Universal'),
    ('datetime', 'Date-Time'),
    ('date', 'Date'),
)

POLL_RESULTS = (
    ('summary', 'Summary'),
    ('complete', 'Complete'),
    ('never', 'Never'),
    ('summary after vote', 'Summary after Vote'),
    ('complete after vote', 'Complete after Vote'),
)


class Poll(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    url = models.CharField(max_length=80, unique=True)
    type = models.CharField(max_length=20, choices=POLL_TYPES, default="normal")
    created = models.DateTimeField(auto_now_add=True)
    """owner_id = models.ForeignKey(Member)"""

    # === Extra settings ==
    due_date = models.DateTimeField()
    anonymous_allowed = models.BooleanField(default=True)
    public_listening = models.BooleanField(default=False)
    require_login = models.BooleanField(default=False)
    require_invitation = models.BooleanField(default=False)
    show_results = models.CharField(max_length=20, choices=POLL_RESULTS, default="complete")
    send_mail = models.BooleanField(default=False)
    one_vote_per_user = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    show_invitations = models.BooleanField(default=True)
    timezone_name = models.CharField(max_length=40, default="Europe/Berlin")

    def __str__(self):
        return u'Poll {}'.format(self.title)


class Choice(models.Model):
    text = models.CharField(max_length=80)
    date = models.DateTimeField()
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return u'Choice {}'.format(self.text)


class ChoiceValue(models.Model):
    title = models.CharField(max_length=80)
    icon = models.CharField(max_length=64)
    color = models.CharField(max_length=6)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return u'ChoiceValue {}'.format(self.title)


class Comment(models.Model):
    text = models.TextField()
    date_created = models.DateTimeField()
    name = models.CharField(max_length=80)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return u'CommentID {} by {}'.format(self.id, self.name)


class PollWatch(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u'Pollwatch of Poll {} and User {}'.format(self.poll_id, self.user_id)


class Vote(models.Model):
    name = models.CharField(max_length=80)
    anonymous = models.BooleanField(default=False)
    date_created = models.DateTimeField()
    comment = models.TextField()
    assigned_by_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='assigning')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u'Vote {}'.format(self.name)


class VoteChoice(models.Model):
    comment = models.TextField()
    value_id = models.ForeignKey(ChoiceValue, on_delete=models.CASCADE)
    vote_id = models.ForeignKey(Vote, on_delete=models.CASCADE)
    choice_id = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return u'VoteChoice {}'.format(self.id)
