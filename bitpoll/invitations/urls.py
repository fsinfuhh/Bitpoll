from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^([a-zA-Z0-9_\-]+)/$', views.invite, name='invitations'),
    re_path(r'^([a-zA-Z0-9_\-]+)/send/$', views.invitation_send, name='invitations_send'),
]