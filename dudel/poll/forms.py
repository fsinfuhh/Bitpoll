from django.forms import ModelForm

from .models import Poll, Choice


class PollCreationForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'type', 'public_listening', 'due_date', 'url']


class DateChoiceCreationForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['date']


class UniversalChoiceCreationForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['text']
