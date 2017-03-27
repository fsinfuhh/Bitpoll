from django.conf.urls import url
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm,\
    password_reset_complete


from .forms import PasswordResetForm
from .views import *


urlpatterns = [
    url(r'^change_email/([a-zA-Z0-9:_-]+)$', change_email,
            name='registration_change_email'),
    url(r'^request_successful/([a-zA-Z0-9.\-_+]+@[a-zA-Z0-9.\-_]+)$', request_successful,
            name='registration_request_successful'),
    url(r'^account$', account_settings, name='registration_account'),

    url(r'^password_reset/$', password_reset, {
        'password_reset_form': PasswordResetForm
    }, name='password_reset'),
    url(r'^password_reset/done$', password_reset_done,
        name='password_reset_done'),
    url(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$',
        password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset/complete', password_reset_complete,
        name='password_reset_complete')
]

if settings.REGISTER_ENABLED:
    urlpatterns += [
        url(r'^request_account$', request_account,
                name='registration_request_account'),
        url(r'^create_account/([a-zA-Z0-9:_-]+)$', create_account,
                name='registration_create_account'),
    ]
