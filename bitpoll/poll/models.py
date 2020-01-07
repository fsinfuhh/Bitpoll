import enum
from smtplib import SMTPRecipientsRefused
from typing import Optional

from django.contrib import messages
from django.contrib.auth.models import Group, AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField

from bitpoll.base.models import BitpollUser
from bitpoll.base.validators import validate_timezone
from bitpoll.poll.util import DateTimePart, PartialDateTime
from django.utils import translation

POLL_TYPES = (
    ('universal', _('Universal')),
    ('datetime', _('Date-Time')),
    ('date', _('Date')),
)

POLL_RESULTS = (
    ('summary', _('Summary')),
    ('complete', _('Complete')),
    ('never', _('Never')),
    ('summary after vote', _('Summary after Vote')),
    ('complete after vote', _('Complete after Vote')),
)


class ResultSorting(enum.IntEnum):
    DATE = 0
    NAME = 1


POLL_RESULT_SORTING = (
    (ResultSorting.DATE.value, _('Date')),
    (ResultSorting.NAME.value, _('Name'))
)


class Poll(models.Model):
    title = models.CharField(max_length=80, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'), help_text=_('You can use <a href="http://daringfireball.net/projects/markdown/" target="_blank">Markdown</a> syntax for formatting.'))
    url = models.SlugField(max_length=80, unique=True)
    type = models.CharField(max_length=20, choices=POLL_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(BitpollUser, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('owning user'))
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('owning group'))

    # === Extra settings ==
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_('due date'))
    anonymous_allowed = models.BooleanField(default=True, verbose_name=_('allow anonymous votes'))
    public_listening = models.BooleanField(default=False, verbose_name=_('public listening'))
    require_login = models.BooleanField(default=False, verbose_name=_('login required'))
    require_invitation = models.BooleanField(default=False, verbose_name=_('invitation required to vote'))
    show_results = models.CharField(max_length=20, choices=POLL_RESULTS, default="complete", verbose_name=_('Show Results'), help_text=_('Owners of this poll and administrators will always see all votes.'))
    one_vote_per_user = models.BooleanField(default=True, verbose_name=_('one vote per user'))
    allow_unauthenticated_vote_changes = models.BooleanField(default=False, verbose_name=_('allow unauthenticated vote changes'))
    allow_comments = models.BooleanField(default=True, verbose_name=_('allow comments'))
    show_invitations = models.BooleanField(default=True, verbose_name=_('show invitations as empty votes'))
    timezone_name = models.CharField(max_length=40, default="Europe/Berlin", validators=[validate_timezone], verbose_name=_('Timezone'))
    use_user_timezone = models.BooleanField(default=False, verbose_name=_('Translate all times to the users timezone'))
    vote_all = models.BooleanField(default=False, verbose_name=_('forbid empty choices'))
    sorting = models.IntegerField(default=0, choices=POLL_RESULT_SORTING, verbose_name=_('Sort results by'))
    hide_participants = models.BooleanField(default=False, verbose_name=_('hide participants'))

    def __str__(self):
        return u'Poll {}'.format(self.title)

    def can_vote(self, user: AbstractUser, request: Optional[HttpRequest] = None, is_edit: bool=False) -> bool:
        """
        Determine if the user is allowed to vote

        :param is_edit: if the vote is an edit
        :param user:
        :param request: the request object or None. if None no messages are printed
        :return:
        """
        has_voted = self.has_voted(user)
        if self.one_vote_per_user and has_voted and not is_edit:
            if request:
                messages.error(request, _("It is only one vote allowed. You have already voted."))
            return False
        elif self.require_login and not user.is_authenticated:
            if request:
                messages.error(request, _("Login required to vote."))
            return False
        elif self.require_invitation and (not user.is_authenticated or not self.invitation_set.filter(user=user).exists()):
            if request:
                messages.error(request, _("You are not allowed to vote in this poll. You have to be invited"))
            return False
        return True

    def has_voted(self, user: AbstractUser) -> bool:
        return user.is_authenticated and Vote.objects.filter(user=user, poll=self).count() > 0

    def get_own_vote(self, user: AbstractUser):
        return Vote.objects.filter(user=user, poll=self)[0]

    def can_edit(self, user: AbstractUser, request: HttpRequest=None) -> bool:
        """
        check if the user can edit this Poll

        :param user: The user to edit the Poll
        :param request:  The request object,
                if this is set a error message will be emitted via the django.messages framework
        :return:
        """
        has_owner = self.group or self.user
        is_owner = self.is_owner(user)

        can_edit = ((not has_owner) or is_owner) and user.is_authenticated or not has_owner
        if request and not can_edit:
            messages.error(
                request, _("You are not allowed to edit this Poll.")
            )
        return can_edit

    def can_watch(self, user: AbstractUser) -> bool:
        if self.can_vote(user) and self.show_results not in ('never', 'summary after vote', 'complete after vote'):
            # If the user can vote and the results are not restricted
            return True
        if self.has_voted(user) and self.show_results not in ('never', ):
            # If the user has voted and can view the results
            return True
        return False

    def is_owner(self, user: AbstractUser):
        return self.user == user or (self.group and user in self.group.user_set.all())

    def get_icon(self):
        if self.type == 'universal':
            return 'list'
        if self.type == 'datetime':
            return 'clock-o'
        if self.type == 'date':
            return 'calendar'

    @property
    def ordered_choices(self):
        return self.choice_set.filter(deleted=False).order_by('sort_key')

    def get_choice_group_matrix(self, tz):
        matrix = [
            choice.get_hierarchy(tz) for choice in self.ordered_choices]
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

    def get_tz_name(self, user: BitpollUser):
        # TODO: local etc beachten (umrechenn auf user...)
        if self.type == 'date':
            # Datepolls are using UTC as timezone
            tz = 'UTC'
        else:
            tz = self.get_tz_name_no_date_utc(user)
        return tz

    def get_tz_name_no_date_utc(self, user: BitpollUser):
        tz = self.timezone_name
        if user.is_authenticated and self.use_user_timezone:
            return user.timezone
        return tz

    def current_user_is_owner(self, request) -> bool:
        if request.user.is_authenticated:
            return self.is_owner(request.user)
        return False

    def user_watches(self, user: BitpollUser) -> bool:
        """
        Check if the user is watching this poll

        :param user: The User in Question
        :return: True if the User watches the Poll
        """
        return user.is_authenticated and PollWatch.objects.filter(poll=self, user=user).count() > 0


class Choice(models.Model):
    text = models.CharField(max_length=80)
    date = models.DateTimeField(null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, db_index=True)
    sort_key = models.IntegerField()
    deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        if self.poll.type == 'universal':
            return self.text
        elif self.poll.type == 'date':
            return self.date.strftime("%Y-%m-%d")
        else:
            return self.date

    @cached_property
    def get_title(self):
        return self.__str__()

    def can_edit(self, user: BitpollUser, request: HttpRequest=None) -> bool:
        return self.poll.can_edit(user, request)

    def get_hierarchy(self, tz):
        if self.date:
            return [PartialDateTime(self.date, DateTimePart.date, tz),
                    PartialDateTime(self.date, DateTimePart.time, tz)]
        return [part.strip() for part in self.text.split("/") if part]

    def votechoice_count(self):
        return self.votechoice_set.filter(value__isnull=False).count()


class ChoiceValue(models.Model):
    title = models.CharField(max_length=80)
    icon = models.CharField(max_length=64, help_text=_('any FontAwesome icon'))
    color = models.CharField(max_length=7, validators=[RegexValidator('#?[a-fA-F0-9]{6}$',
                                                                      message=_("Give an HTML color in hex notation (#5500ff)"))])
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name=_('Weight'), help_text=_('usually between 0 and 1'))
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return u'ChoiceValue {}'.format(self.title)

    def can_edit(self, user: BitpollUser, request=None) -> bool:
        return self.poll.can_edit(user, request)

    def votechoice_count(self):
        return self.poll.vote_set.filter(votechoice__value=self).count()


class Comment(models.Model):
    text = MarkdownField(help_text=_('You can use <a href="http://daringfireball.net/projects/markdown/" target="_blank">Markdown</a> syntax for formatting.'))
    date_created = models.DateTimeField()
    name = models.CharField(max_length=80)
    user = models.ForeignKey(BitpollUser, on_delete=models.CASCADE, null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return u'CommentID {} by {}'.format(self.id, self.name)

    def can_edit(self, user: BitpollUser) -> bool:
        is_owner = user == self.user

        return user.is_authenticated and is_owner

    def can_delete(self, user: BitpollUser) -> bool:
        is_poll_owner = self.poll.user == user

        return is_poll_owner or self.can_edit(user)


class Vote(models.Model):
    name = models.CharField(max_length=80)
    anonymous = models.BooleanField(default=False, help_text=_("Post as anonymous vote"))
    date_created = models.DateTimeField()
    comment = models.TextField(blank=True)
    assigned_by = models.ForeignKey(BitpollUser, on_delete=models.CASCADE, null=True, related_name='assigning')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(BitpollUser, on_delete=models.CASCADE, null=True, blank=True)

    def can_edit(self, user: BitpollUser) -> bool:
        """
        Determine if the user can edit the Vote

        :param user: is this user allowed to edit the vote
        :return:
        """
        if user.is_authenticated and (self.user == user or self.poll.can_edit(user)):
            return True
        if not self.user and (self.poll.can_edit(user) or self.poll.allow_unauthenticated_vote_changes):
            return True
        return False

    def can_delete(self, user: BitpollUser) -> bool:
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
    
    @property
    def display_name(self) -> str:
        """Name of user if assigned, name field or anonymous else."""
        if self.anonymous:
            return _('Anonymous')
        if self.user:
            # return '{} ({})'.format(self.user.first_name, self.user.username)
            return self.user.get_displayname()
        return self.name

    def __str__(self):
        return u'Vote {}'.format(self.display_name)


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

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(BitpollUser, on_delete=models.CASCADE)

    def send(self, request, vote: Vote):
        old_lang = translation.get_language()
        translation.activate(self.user.language)
        link = reverse('poll', args=(self.poll.url,))
        if vote.anonymous:
            username = _("Annonymus")
        elif vote.user:
            username = vote.user.username
        else:
            username = vote.name
        email_content = render_to_string('poll/mail_watch.txt', {
            'receiver': self.user.username,
            'user': username if self.poll.show_results == "complete" else _("by an user"),
            'poll': self.poll.title,
            'link': link,
            'hide_participants': self.poll.hide_participants  # TODO: simplify merge with usernameshadowing above
        })
        try:
            send_mail(_("New votes for {}".format(self.poll.title)), email_content, None,
                      [self.user.email])
        except SMTPRecipientsRefused:
            translation.activate(old_lang)
            messages.error(
                request, _("The mail server had an error sending the notification to {}".format(
                    self.user.username))
            )
        translation.activate(old_lang)

    def __str__(self):
        return u'Pollwatch of Poll {} and User {}'.format(self.poll_id, self.user_id)
