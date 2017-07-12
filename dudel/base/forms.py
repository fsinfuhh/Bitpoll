from django.forms import ModelForm

from .models import BitpollUser


class BitpollUserSettingsForm(ModelForm):
    class Meta:
        model = BitpollUser
        fields = ['auto_watch', 'email_invitation', 'timezone', 'language']
