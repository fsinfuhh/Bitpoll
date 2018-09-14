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


class PasswordResetForm(forms.Form):
    """
    This is just copied from django/contrib/auth/forms.py with email
    changed to real_email.
    """
    email = forms.EmailField(label=_("Email"), max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                c.update(extra_email_context)

            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)

            if html_email_template_name:
                html_email = loader.render_to_string(html_email_template_name, c)
            else:
                html_email = None
            send_mail(subject, email, from_email, [user.email], html_message=html_email)
