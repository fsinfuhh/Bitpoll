from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^$', views.index, name='index'),
    url(r'^imprint/$', views.imprint, name='imprint'),
    url(r'^about/$', views.about, name='about'),
    url(r'^licenses/$', views.licenses, name='base_licenses'),
    url(r'^technical_info/$', views.tecnical, name='technical'),
    url(r'^autocomplete$', views.autocomplete, name='base_autocomplete'),
    url(r'^problems$', views.problems, name='base_problems'),
]
