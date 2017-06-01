from django.forms import ModelForm, CharField, Form
from datetimewidget.widgets import DateTimeWidget

from .models import Poll, Choice, ChoiceValue, Comment


class PollCreationForm(ModelForm):
    class Meta:
        model = Poll
        fields = [
            'title',
            'type',
            'public_listening',
            'due_date',
            'url',
            'description',
            'anonymous_allowed',
            'require_login',
            'require_invitation',
            'one_vote_per_user',
            'vote_all'
        ]
        widgets = {
            'due_date': DateTimeWidget(
                attrs={'id': "id_due_date"}, usel10n=True, bootstrap_version=3)
        }


class PollCopyForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'url']
        widgets = {
            'due_date': DateTimeWidget(
                attrs={'id': "id_due_date"}, usel10n=True, bootstrap_version=3)
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
        fields = [
            'title',
            'due_date',
            'show_results',
            'timezone_name',
            'description',
            'allow_comments',
            'anonymous_allowed',
            'require_login',
            'require_invitation',
            'one_vote_per_user',
            'show_invitations',
            'group',
            'public_listening',
            'vote_all',
            'use_user_timezone',
        ]
        widgets = {
            'due_date': DateTimeWidget(
                attrs={'id': "id_due_date"}, usel10n=True, bootstrap_version=3)
        }


class PollDeleteForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'description'] #TODO: das sollte kein model form sein


class ChoiceValueForm(ModelForm):
    class Meta:
        model = ChoiceValue
        fields = ['title', 'icon', 'color', 'weight']

    def clean_color(self):
        color = self.cleaned_data['color']
        if color[0] == '#':
            return color[1:]
        return color


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'text']
