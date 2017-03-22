from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^$', views.index, name='index'),
    url(r'^imprint/$', views.imprint, name='imprint'),
    url(r'^licenses/$', views.licenses, name='base_licenses'),
    url(r'^tecnical_info/$', views.tecnical, name='tecnical'),
]