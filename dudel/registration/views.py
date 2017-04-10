from smtplib import SMTPRecipientsRefused

from django.core import signing
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from dudel.base.models import DudelUser
from dudel.registration.forms import (RegisterForm,
                                        PasswordForm, NickChangeForm,
                                        EmailChangeForm)

TOKEN_MAX_AGE = 3600 * 24


def request_account(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data.update({'action': 'request_account'})
            return _finish_account_request(request, data)
    else:
        form = RegisterForm()

    return TemplateResponse(request, 'registration/request_account.html', {
            'user_form': form,
        })


def request_successful(request, email):
    return TemplateResponse(request, 'registration/request_successful.html', {
        'email': email
    })


def create_account(request, info_token):
    if request.user.is_authenticated():
        return redirect('home')
    try:
        info = signing.loads(info_token, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        return TemplateResponse(request, 'registration/token_expired.html')
    except signing.BadSignature:
        return TemplateResponse(request, 'registration/token_invalid.html')

    username = info['username']

    if DudelUser.objects.filter(username=username).exists():
        messages.warning(request,_("This User already exists"))
        return redirect('login')

    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            first_name = info.get('first_name')
            last_name = info.get('last_name')
            if not (first_name and last_name):
                return TemplateResponse(request, 'registration/token_invalid.html')
            email = info['email']
            user = DudelUser(username=username,
                             email=email,
                             first_name=first_name,
                             last_name=last_name,
                             email_invitation=info['email_invitation'],
                             #TODO: weitere felder??
                             )
            user.set_password(form.cleaned_data['password1'])
            user.save()
            user.backend='django.contrib.auth.backends.ModelBackend'

            login(request, user)
            return redirect('home')
    else:
        form = PasswordForm()

    return TemplateResponse(request, 'registration/create_account.html', {
        'form': form,
        'username': username
    })


@login_required
def account_settings(request):
    password_change_form = PasswordChangeForm(request.user)
    nick_change_form = NickChangeForm(request.user)
    email_change_form = EmailChangeForm(request.user)

    form = request.POST.get('form')
    if form == 'change_pw':
        password_change_form = PasswordChangeForm(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            messages.success(request, _("Password was changed."))
            return redirect('registration_account')
    elif form == 'change_nick':
        nick_change_form = NickChangeForm(request.user, request.POST)
        if nick_change_form.is_valid():
            nick_change_form.save()
            messages.success(request, _('Your nickname is now {}.').format(
                nick_change_form.cleaned_data['nickname']))
            return redirect('registration_account')
    elif form == 'change_email':
        email_change_form = EmailChangeForm(request.user, request.POST)
        if email_change_form.is_valid():
            return _verify_email(request,
                                 email_change_form.cleaned_data['email'])
    
    return TemplateResponse(request, 'registration/account.html', {
        'password_change_form': password_change_form,
        'nick_change_form': nick_change_form,
        'email_change_form': email_change_form,
        'username': request.user.username,
    })


@login_required
def change_email(request, token):
    try:
        data = signing.loads(token, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        return TemplateResponse(request, 'registration/token_expired.html')
    except signing.BadSignature:
        return TemplateResponse(request, 'registration/token_invalid.html')
    if request.user.username != data.get('username'):
        return TemplateResponse(request, 'registration/token_invalid.html')
    email = data.get('email')
    try:
        validate_email(email)
    except ValidationError:
        return TemplateResponse(request, 'registration/token_invalid.html')
    request.user.email = email
    request.user.save()

    messages.success(request, _('Your email address has been changed.'))
    return redirect('registration_account')


def _verify_email(request, email):
    token = signing.dumps({
        'email': email,
        'username': request.user.username,
    })
    url_path = reverse('registration_change_email', args=(token,))
    link = request.build_absolute_uri(url_path)
    email_content = render_to_string('registration/email_verify.txt', {
        'username': request.user.username,
        'email': email,
        'link': link,
    })
    return _send_mail_or_error_page(_('Verify this address for %s' % settings.SITE_NAME),
                                    email_content, email, request)


def _finish_account_request(request, info):
    email = info['email']
    token = signing.dumps(info)
    url_path = reverse('registration_create_account', args=(token,))
    activation_link = request.build_absolute_uri(url_path)
    email_content = render_to_string('registration/create_email.txt', {
        'activation_link': activation_link
    })
    return _send_mail_or_error_page(_('Account creation at %s' % settings.SITE_NAME),
                                    email_content, email, request)


def _send_mail_or_error_page(subject, content, address, request):
    try:
        send_mail(subject, content, None, [address])
        if settings.DEBUG:
            print(u"VALIDATION MAIL to {0}\nSubject: {1}\n{2}".format(
                address, subject, content))
    except SMTPRecipientsRefused as e:
        wrong_email, (error_code, error_msg) = e.recipients.items()[0]
        unknown = 'User unknown' in error_msg
        if not unknown:
            error_email_content = u'{0}: {1}'.format(e.__class__.__name__,
                                                     repr(e.recipients))
            send_mail(
                    _('Registration: Sending mail failed: {}'.format(address)),
                    error_email_content,
                    None,
                    [settings.TEAM_EMAIL])
        return TemplateResponse(request, 'registration/email_error.html', {
            'unknown': unknown,
            'error_code': error_code,
            'error_msg': error_msg,
            'recipient': wrong_email
        })

    return redirect('registration_request_successful', address)
