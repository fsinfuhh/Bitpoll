from pytz import all_timezones
from time import strptime

from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, Form, HiddenInput, IntegerField, ChoiceField
from django.utils.translation import ugettext_lazy as _

from .models import Poll, Choice, ChoiceValue, Comment, Vote


class MultipleTemporalBaseField(CharField):
    format = ""
    message = ""

    def validate(self, values):
        super().validate(values)
        for value in values.split(','):
            try:
                strptime(value.strip(), self.format)
            except (ValueError, TypeError):
                raise ValidationError(
                    self.message,
                    code='invalid',
                    params={'value': value.strip()}
                )


class DatesField(MultipleTemporalBaseField):
    format = "%Y-%m-%d"
    message = _('could not parse the date: "%(value)s", the format is YYY-MM-DD separated by commas.')


class TimesField(MultipleTemporalBaseField):
    format = "%H:%M"
    message = _('could not parse the time: "%(value)s", the format is HH:MM separated by commas.')


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
            'allow_unauthenticated_vote_changes',
            'one_vote_per_user',
            'vote_all',
        ]


class PollCopyForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'url']


class DateChoiceCreationForm(Form):
    dates = DatesField()


class UniversalChoiceCreationForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['text']


class DTChoiceCreationDateForm(Form):
    dates = DatesField()


class DTChoiceCreationTimeForm(Form):
    """def __init__(self, date, *args, **kwargs):
        super(DTChoiceCreationTimeForm, self).__init__(*args, **kwargs)
        self.date.initial = date"""

    dates = DatesField()
    times = TimesField()


class TimezoneChoiceField(ChoiceField):
    def __init__(self, **kwargs):
        kwargs.pop('max_length')
        super().__init__(choices=[x for x in zip(all_timezones, all_timezones)], **kwargs)


class PollSettingsForm(ModelForm):
    user = CharField(max_length=100, required=False, label=_('Name'))

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
            'allow_unauthenticated_vote_changes',
            'one_vote_per_user',
            'show_invitations',
            'group',
            'public_listening',
            'vote_all',
            'hide_participants',
            'use_user_timezone',
            'sorting',
        ]
        field_classes = {
            'timezone_name': TimezoneChoiceField,
        }


class PollDeleteForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'description']  # TODO: das sollte kein model form sein


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
    spam_key = CharField(widget=HiddenInput(), required=False)
    spam_answer = IntegerField(required=False)

    class Meta:
        model = Comment
        fields = ['name', 'text']


class VoteForm(ModelForm):
    name = CharField(required=False, max_length=100)

    class Meta:
        model = Vote
        fields = ['comment', 'anonymous']


class VoteFormUser(VoteForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True
