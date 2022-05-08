from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.urls import path

from .views import *


urlpatterns = [
    re_path(r'^change_email/([a-zA-Z0-9:_-]+)$', change_email,
        name='registration_change_email'),
    re_path(r'^request_successful/([a-zA-Z0-9.\-_+]+@[a-zA-Z0-9.\-_]+)$', request_successful,
        name='registration_request_successful'),
    path('account', account_settings, name='registration_account'),
]

# TODO: own settings value for changing password? If yes: remember to change template ifs when to show the link
if settings.REGISTER_ENABLED:
    urlpatterns += [
        path('password_reset/', auth_views.PasswordResetView.as_view(), {
            'password_reset_form': PasswordResetForm
        }, name='password_reset'),
        path('password_reset/done', auth_views.PasswordResetDoneView.as_view(),
            name='password_reset_done'),
        path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        re_path(r'^password_reset/complete', auth_views.PasswordResetCompleteView.as_view(),
            name='password_reset_complete')
    ]

if settings.REGISTER_ENABLED:
    urlpatterns += [
        path('request_account', request_account,
            name='registration_request_account'),
        re_path(r'^create_account/([a-zA-Z0-9:_-]+)$', create_account,
            name='registration_create_account'),
    ]
