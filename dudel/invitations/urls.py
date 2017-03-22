from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^([a-zA-Z0-9_\-]+)/$', views.invite, name='invitations'),
    url(r'^([a-zA-Z0-9_\-]+)/send/$', views.invitation_send, name='invitations_send'),
]