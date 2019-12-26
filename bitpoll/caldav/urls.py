from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^change/$', views.change_calendar, name='change_calendar'),
    ]
