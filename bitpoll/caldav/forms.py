from django.forms import ModelForm, CharField, PasswordInput

from .models import DavCalendar


class DavCalendarForm(ModelForm):
    user = CharField(required=False)
    password = CharField(widget=PasswordInput, required=False)

    class Meta:
        model = DavCalendar
        fields = [
            'url',
            'name',
        ]
