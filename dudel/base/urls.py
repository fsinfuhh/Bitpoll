from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^$', views.index, name='index'),
]