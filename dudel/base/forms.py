from django.forms import ModelForm

from .models import DudelUser


class DudelUserSettingsForm(ModelForm):
    class Meta:
        model = DudelUser
        fields = ['auto_watch', 'email_invitation', 'timezone', 'language']
