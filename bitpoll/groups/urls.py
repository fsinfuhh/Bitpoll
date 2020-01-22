from django.urls import path, include, re_path

from .models import group_name_regex
from .views import *

urlpatterns = [
    path('', index, name='groups_index'),
    path('create', create, name='groups_create'),
    re_path('^g/(?P<group_name>{})/'.format(group_name_regex), include([
        path('', show, name='groups_show'),
        path('leave', leave, name='groups_leave'),
        path('invite', invite, name='groups_invite'),
        path('action/<int:member_pk>', group_action,
            name='groups_action'),
        ])),
    path('invitations/<int>/action', invitation_action,
            name='groups_invitation_action'),
    path('invitations/<int>/withdraw', withdraw_invite,
            name='groups_withdraw_invite'),
]
