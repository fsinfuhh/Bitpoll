from django.forms import ModelForm, CharField, Form

from .models import Poll, Choice, ChoiceValue
from datetimewidget.widgets import DateTimeWidget


class PollCreationForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'type', 'public_listening', 'due_date', 'url', 'description', 'anonymous_allowed',
                  'require_login', 'require_invitation', 'one_vote_per_user']
        widgets = {
            'due_date': DateTimeWidget(attrs={'id': "id_due_date"}, usel10n=True, bootstrap_version=3)
        }


class PollCopyForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'url']
        widgets = {
            'due_date': DateTimeWidget(attrs={'id': "id_due_date"}, usel10n=True, bootstrap_version=3)
        }


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
        widgets = {
            'due_date': DateTimeWidget(attrs={'id': "id_due_date"}, usel10n=True, bootstrap_version=3)
        }


class PollDeleteForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'description'] #TODO: das sollte kein model form sein


class ChoiceValueForm(ModelForm):
    class Meta:
        model = ChoiceValue
        fields = ['title', 'icon', 'color', 'weight']