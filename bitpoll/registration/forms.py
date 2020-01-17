import re

from django import forms
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site


from bitpoll.base.models import BitpollUser


class RegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = BitpollUser
        fields = ['username', 'first_name', 'last_name', 'email', 'auto_watch',
                  'email_invitation']
        #  TODO for later: 'timezone', 'language',


class CheckPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CheckPasswordForm, self).__init__(*args, **kwargs)

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if not self.user.check_password(password):
                raise forms.ValidationError(_("Wrong password."))
        return password


class NickChangeForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        nickname = re.sub(r'(.+)\s\((.+)\)$', r'\1', user.username)
        kwargs['initial'] = {
            'nickname': nickname
        }
        super(NickChangeForm, self).__init__(*args, **kwargs)

    nickname = forms.CharField(max_length=20)

    def save(self):
        ldap_user = self.user.get_ldapuser()
        ldap_user.display_name = u"{} ({})".format(
            self.cleaned_data['nickname'], self.user.username)
        ldap_user.save()


class EmailChangeForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, user, *args, **kwargs):
        kwargs['initial'] = {
            'email': user.email,
        }
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if BitpollUser.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(
                _('This address is already associated with an account.'))

        return email
