from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^invitations/([a-zA-Z0-9_\-]+)/$', views.invite, name='invitations'),
    url(r'^invitations_send/([a-zA-Z0-9_\-]+)/$', views.invitation_send, name='invitations_send'),
]