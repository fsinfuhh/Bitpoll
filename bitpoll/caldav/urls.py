from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^change/$', views.change_callendar, name='change_calendar'),
    ]
