from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, Form, HiddenInput, IntegerField, ChoiceField, BooleanField, TextInput, \
    SplitDateTimeField, SplitDateTimeWidget
from django.utils.translation import ugettext_lazy as _
from pytz import all_timezones
from time import strptime

from .models import Poll, Choice, ChoiceValue, Comment, Vote
from .spam_util import get_spam_label


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


class CustomDateTimeWidget(SplitDateTimeWidget):
    def __init__(self):
        super().__init__(date_attrs={'placeholder': _("Date")},
                         time_attrs={'placeholder': _("Time"), 'pattern': '[0-2][0-9]:[0-5][0-9]:[0-5][0-9]',
                                     'step': 1},
                         date_format="%Y-%m-%d")
        self.widgets[0].input_type = 'date'
        self.widgets[1].input_type = 'time'


class CustomDateTimeField(SplitDateTimeField):
    widget = CustomDateTimeWidget


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
        field_classes = {
            'due_date': CustomDateTimeField
        }


class PollCopyForm(ModelForm):
    copy_choices = BooleanField(required=False, label=_('Copy Choices'))
    copy_invitations = BooleanField(required=False, label=_('Copy Invitations'))
    create_invitations_from_votes = BooleanField(required=False, label=_('Create invitations from existing Votes'))
    copy_answer_values = BooleanField(required=False, label=_('Copy answer values'))
    reset_ownership = BooleanField(required=False, label=_('Reset ownership'))
    date_shift = IntegerField(label=_('Shift by X days'), initial=0)

    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'url']
        field_classes = {
            'due_date': CustomDateTimeField
        }


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
            'due_date': CustomDateTimeField
        }


class PollDeleteForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'due_date', 'description']  # TODO: das sollte kein model form sein


class ChoiceValueForm(ModelForm):
    class Meta:
        model = ChoiceValue
        fields = ['title', 'icon', 'color', 'weight']
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }

    def clean_color(self):
        color = self.cleaned_data['color']
        if color[0] == '#':
            return color[1:]
        return color


class CommentForm(ModelForm):
    spam_key = CharField(widget=HiddenInput(), required=False)
    spam_answer = IntegerField(required=False)

    def __init__(self, user, *args, **kwargs):
        if user.is_authenticated:
            initial = {'name': user.get_displayname()}
        else:
            initial = None
        super().__init__(*args, initial=initial, **kwargs)
        if user.is_authenticated:
            self.fields['name'].widget.attrs['readonly'] = True
        else:
            self.fields['name'].widget.attrs['placeholder'] = _("Display Name")
        self.fields['text'].widget.attrs['placeholder'] = _("Comment Text")
        self.fields['spam_answer'].widget.attrs['placeholder'] = _("Result of equation above")

    def set_spam_challenge(self, spam_dict):
        self.fields['spam_answer'].label = get_spam_label(spam_dict)
        self.fields['spam_key'].widget.attrs['value'] = spam_dict['key']
        self.fields['spam_answer'].widget.attrs['required'] = True

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
