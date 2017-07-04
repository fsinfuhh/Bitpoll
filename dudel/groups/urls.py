from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', index, name='groups_index'),
    url(r'^create$', create, name='groups_create'),
    url(r'^g/([a-zA-Z0-9_-]+)/$', show, name='groups_show'),
    url(r'^g/([a-zA-Z0-9_-]+)/leave$', leave, name='groups_leave'),
    url(r'^g/([a-zA-Z0-9_-]+)/invite$', invite, name='groups_invite'),
    url(r'^g/([a-zA-Z0-9_-]+)/action/(\d+)$', group_action,
            name='groups_action'),
    url(r'^invitations/(\d+)/action', invitation_action,
            name='groups_invitation_action'),
    url(r'^invitations/(\d+)/withdraw', withdraw_invite,
            name='groups_withdraw_invite'),
]
