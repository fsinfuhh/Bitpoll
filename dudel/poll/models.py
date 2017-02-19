from django.db import models
from django.contrib.auth.models import Group, User

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
    description = models.TextField()
    url = models.CharField(max_length=80, unique=True)
    type = models.CharField(max_length=20, choices=POLL_TYPES, default="universal")
    created = models.DateTimeField(auto_now_add=True)
    """owner_id = models.ForeignKey(Member)"""

    # === Extra settings ==
    due_date = models.DateTimeField(null=True, blank=True)
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

    def get_icon(self):
        if self.type == 'universal':
            return 'list'
        if self.type == 'datetime':
            return 'clock-o'
        if self.type == 'date':
            return 'calendar'

    def get_choice_group_matrix(self):
        matrix = [
            choice.get_hierarchy() for choice in self.choice_set.all().order_by(
                'sort_key')]
        matrix = [[[item, 1, 1] for item in row] for row in matrix]
        if not matrix:
            return [[]]
        width = max(len(row) for row in matrix)

        def fill(row, length):
            if len(row) >= length: return
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


class Choice(models.Model):
    text = models.CharField(max_length=80)
    date = models.DateTimeField(null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    sort_key = models.IntegerField()

    def __str__(self):
        if self.poll.type == 'universal':
            return self.text
        else:
            return str(self.date)

    def get_hierarchy(self):
        if self.date:
            return [PartialDateTime(self.date, DateTimePart.date),
                    PartialDateTime(self.date, DateTimePart.time)]
        else:
            return [part.strip() for part in self.text.split("/") if part]


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    # TODO allow null for user -> comment creation possible

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
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='assigning')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def can_edit(self, user: User) -> bool:
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

    def can_delete(self, user: User) -> bool:
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
