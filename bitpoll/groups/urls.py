from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', index, name='groups_index'),
    path('create', create, name='groups_create'),
    re_path(r'^g/([a-zA-Z0-9_\-\.]+)/$', show, name='groups_show'),
    re_path(r'^g/([a-zA-Z0-9_\-\.]+)/leave$', leave, name='groups_leave'),
    re_path(r'^g/([a-zA-Z0-9_\-\.]+)/invite$', invite, name='groups_invite'),
    re_path(r'^g/([a-zA-Z0-9_\-\.]+)/action/(\d+)$', group_action,
            name='groups_action'),
    re_path(r'^invitations/(\d+)/action', invitation_action,
            name='groups_invitation_action'),
    re_path(r'^invitations/(\d+)/withdraw', withdraw_invite,
            name='groups_withdraw_invite'),
]
