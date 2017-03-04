from django.forms import ModelForm, CharField, Form

from .models import Poll, Choice


class PollCreationForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'type', 'public_listening', 'due_date', 'url']


class PollCopyForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'url']


class DateChoiceCreationForm(Form):
    dates = CharField()


class UniversalChoiceCreationForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['text']


class DTChoiceCreationDateForm(Form):
    dates = CharField()


class DTChoiceCreationTimeForm(Form):
    """def __init__(self, date, *args, **kwargs):
        super(DTChoiceCreationTimeForm, self).__init__(*args, **kwargs)
        self.date.initial = date"""

    dates = CharField()
    times = CharField()


class PollSettingsForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'show_results', 'timezone_name', 'description', 'allow_comments',
                  'anonymous_allowed', 'require_login', 'require_invitation', 'one_vote_per_user', 'show_invitations',
                  'group', 'public_listening']


class PollDeleteForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'description']
