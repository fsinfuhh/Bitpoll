from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^([a-zA-Z0-9_\-]+)$', views.ivitations, name='invitations'),
    url(r'^([a-zA-Z0-9_\-]+)/(\d+)/delete$', views.delete_invitation, name='invitations_deleteInvitation'),
    url(r'^([a-zA-Z0-9_\-]+)/(\d+)/resend$', views.resend_invitation, name='invitations_resendInvitation'),
    url(r'^([a-zA-Z0-9_\-]+)/resend$', views.resend, name='invitations_resend'),
]