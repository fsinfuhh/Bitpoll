from smtplib import SMTPRecipientsRefused

from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField

from dudel.base.models import DudelUser
from dudel.base.validators import validate_timezone
from dudel.poll.util import DateTimePart, PartialDateTime

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
    description = models.TextField(blank=True)
    url = models.SlugField(max_length=80, unique=True)
    type = models.CharField(max_length=20, choices=POLL_TYPES, default="universal")
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(DudelUser, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    """owner_id = models.ForeignKey(Member)"""

    # === Extra settings ==
    due_date = models.DateTimeField(null=True, blank=True)
    anonymous_allowed = models.BooleanField(default=True)
    public_listening = models.BooleanField(default=False)
    require_login = models.BooleanField(default=False)
    require_invitation = models.BooleanField(default=False)
    show_results = models.CharField(max_length=20, choices=POLL_RESULTS, default="complete")
    send_mail = models.BooleanField(default=False)
    one_vote_per_user = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    show_invitations = models.BooleanField(default=True)
    timezone_name = models.CharField(max_length=40, default="Europe/Berlin", validators=[validate_timezone])

    def __str__(self):
        return u'Poll {}'.format(self.title)

    def can_vote(self, user: DudelUser, request, is_edit: bool=False) -> bool:
        """
        Determine if the user is allowed to vote

        :param is_edit: if the vote is an edit
        :param user:
        :param request:
        :return:
        """
        has_voted = self.has_voted(user)
        if self.one_vote_per_user and has_voted and not is_edit:
            messages.error(request, _("It is only one vote allowed. You have already voted."))
            return False
        elif self.require_login and not user.is_authenticated:
            messages.error(request, _("Login required to vote."))
            return False
        elif self.require_invitation and (not user.is_authenticated or user not in self.invitation_set.all().values('user')):
            messages.error(request, _("You are not allowed to vote in this poll. You have to be invited"))
            return False
        return True

    def has_voted(self, user: DudelUser) -> bool:
        return user.is_authenticated and Vote.objects.filter(user=user, poll=self).count() > 0

    def get_own_vote(self, user: DudelUser):
        return Vote.objects.filter(user=user, poll=self)[0]

    def can_edit(self, user: DudelUser):
        has_owner = self.group or self.user
        is_owner = user == self.user
        if self.group:
            is_group_member = user in self.group.user_set
        else:
            is_group_member = False

        return ((not has_owner) or is_group_member or is_owner) and user.is_authenticated() or not has_owner

    def can_listen(self, user: DudelUser):
        if self.public_listening:
            return True
        elif user.is_authenticated and user in self.invitation_set.all().values('user'):
            return True
        elif self.can_edit(user):
            return True
        return False

    def get_icon(self):
        if self.type == 'universal':
            return 'list'
        if self.type == 'datetime':
            return 'clock-o'
        if self.type == 'date':
            return 'calendar'

    def get_choice_group_matrix(self, tz):
        matrix = [
            choice.get_hierarchy(tz) for choice in self.choice_set.filter(deleted=False).order_by(
                'sort_key')]
        matrix = [[[item, 1, 1] for item in row] for row in matrix]
        if not matrix:
            return [[]]
        width = max(len(row) for row in matrix)

        def fill(row, length):
            if len(row) >= length:
                return
            row.append([None, 1, 1])
            fill(row, length)

        for row in matrix:
            fill(row, width)

        # Merge None left to determine depth
        for i in range(width-1, 0, -1):
            for row in matrix:
                if row[i][0] is None:
                    row[i-1][1] = row[i][1] + 1

        # Merge items up and replace by None
        for i in range(len(matrix)-1, 0, -1):
            for j in range(width):
                if matrix[i][j][0] == matrix[i-1][j][0] and matrix[i][j][1] == matrix[i-1][j][1]:
                    matrix[i-1][j][2] = matrix[i][j][2] + 1
                    matrix[i][j][0] = None

        # cut off time column in day mode, only use date field
        if self.type == 'date':
            matrix = [[row[0]] for row in matrix]

        return matrix

    def get_tz_name(self, user):
        # TODO: local etc beachten (umrechenn auf user...)
        tz = self.timezone_name
        if self.type == 'date':
            # Datepolls are using UTC as timezone
            tz = 'UTC'
        return tz


class Choice(models.Model):
    text = models.CharField(max_length=80)
    date = models.DateTimeField(null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    sort_key = models.IntegerField()
    deleted = models.BooleanField(default=False)

    def __str__(self):
        if self.poll.type == 'universal':
            return self.text
        else:
            return str(self.date)

    def can_edit(self, user):
        return self.poll.can_edit(user)

    def get_hierarchy(self, tz):
        if self.date:
            return [PartialDateTime(self.date, DateTimePart.date, tz),
                    PartialDateTime(self.date, DateTimePart.time, tz)]
        return [part.strip() for part in self.text.split("/") if part]

    def votechoice_count(self):
        return self.votechoice_set.filter(value__isnull=False).count()


class ChoiceValue(models.Model):
    title = models.CharField(max_length=80)
    icon = models.CharField(max_length=64)
    color = models.CharField(max_length=6, validators=[RegexValidator('^[a-fA-F0-9]{6}$',
                                                                      message=_("Give an HTML color without the #"))])
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return u'ChoiceValue {}'.format(self.title)

    def can_edit(self, user):
        return self.poll.can_edit(user)

    def votechoice_count(self):
        return self.poll.vote_set.filter(votechoice__value=self).count()


class Comment(models.Model):
    text = MarkdownField()
    date_created = models.DateTimeField()
    name = models.CharField(max_length=80)
    user = models.ForeignKey(DudelUser, on_delete=models.CASCADE, null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return u'CommentID {} by {}'.format(self.id, self.name)

    def can_edit(self, user: DudelUser) -> bool:
        is_owner = user == self.user

        return user.is_authenticated() and is_owner

    def can_delete(self, user: DudelUser) -> bool:
        is_poll_owner = self.poll.user == user

        return is_poll_owner or self.can_edit(user)


class Vote(models.Model):
    name = models.CharField(max_length=80)
    anonymous = models.BooleanField(default=False)
    date_created = models.DateTimeField()
    comment = models.TextField()
    assigned_by = models.ForeignKey(DudelUser, on_delete=models.CASCADE, null=True, related_name='assigning')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(DudelUser, on_delete=models.CASCADE, null=True, blank=True)

    def can_edit(self, user: DudelUser) -> bool:
        """
        Determine if the user can edit the Vote

        :param user: is this user allowed to edit the vote
        :return:
        """
        if user.is_authenticated and self.user == user:
            return True
        if not self.user:
            return True
        return False

    def can_delete(self, user: DudelUser) -> bool:
        """
        Determine if the user can delete the Vote

        :param user:
        :return:
        """
        #if self.poll.owner == user:  # TODO: gruppen, owner algemein
        #    return True
        if user.is_anonymous:
            return False
        return self.can_edit(user)

    def get_choices(self):
        """
        Helper to get the votechoices with missing fields as None
        TODO: should be possible to replace it with one database querry
        :return:
        """
        vote_choices = self.votechoice_set.filter(choice__deleted=False).order_by('choice__sort_key').select_related()
        ret = []
        choices = self.poll.choice_set.filter(deleted=False).order_by('sort_key')
        i = 0
        for vote_choice in vote_choices:
            while vote_choice.choice.pk != choices[i].pk:
                ret.append(None)  # TODO: was schlaueres einfügen?
                i += 1
            ret.append(vote_choice)
            i += 1
        while i < len(choices):
            ret.append(None)
            i += 1
        return ret

    def __str__(self):
        return u'Vote {}'.format(self.name)


class VoteChoice(models.Model):
    class Meta:
        unique_together = ('vote', 'choice')

    comment = models.TextField()
    value = models.ForeignKey(ChoiceValue, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return u'VoteChoice {}'.format(self.id)


class PollWatch(models.Model):
    class Meta:
        unique_together = ('poll', 'user')

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(DudelUser, on_delete=models.CASCADE)

    def send(self, request, vote: Vote):
        link = reverse('poll', args=(self.poll.url,))
        email_content = render_to_string('poll/mail_watch.txt', {
            'receiver': self.user.username,
            'user': vote.user.username if self.poll.show_results == "complete" else _("by an user"),
            'poll': self.poll.title,
            'link': link,
        })
        try:
            send_mail("New votes for {}".format(self.poll.title), email_content, None,
                      [self.user.email])
        except SMTPRecipientsRefused:
            messages.error(
                request, _("The mail server had an error sending the notification to {}".format(
                    self.user.username))
            )

    def __str__(self):
        return u'Pollwatch of Poll {} and User {}'.format(self.poll_id, self.user_id)
