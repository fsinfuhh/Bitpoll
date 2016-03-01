from django.forms import ModelForm, CharField, Form

from .models import Poll, Choice


class PollCreationForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'type', 'public_listening', 'due_date', 'url']


class DateChoiceCreationForm(Form):
    fields = CharField()


class UniversalChoiceCreationForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['text']


class DTChoiceCreationDateForm(Form):
    date = CharField()


class DTChoiceCreationTimeForm(Form):
    #def __init__(self, date, *args, **kwargs):
    #    super(DTChoiceCreationTimeForm, self).__init__(*args, **kwargs)
    #    self.date.initial = date

    date = CharField()
    time = CharField()
