from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^change/$', views.change_calendar, name='change_calendar'),
    url(r'^edit/(\d+)/save/$', views.change_calendar, name='edit_save_calendar'),
    url(r'^edit/(\d+)/$', views.edit_calendar, name='edit_calendar'),
    ]
