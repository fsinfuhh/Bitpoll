from django.urls import path, re_path

from . import views

urlpatterns = [
    path('change/', views.change_calendar, name='change_calendar'),
    re_path(r'^edit/(\d+)/save/$', views.change_calendar, name='edit_save_calendar'),
    re_path(r'^edit/(\d+)/$', views.edit_calendar, name='edit_calendar'),
    re_path(r'^edit/(\d+)/delete$', views.delete_calendar_confirm, name='delete_calendar_confirm'),
]
