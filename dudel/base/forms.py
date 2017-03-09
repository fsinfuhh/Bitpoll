from django.forms import ModelForm

from .models import DudelUser


class DudelUserForm(ModelForm):
    class Meta:
        model = DudelUser
        fields = ['timezone', 'language', 'auto_watch', 'email_invitation']
