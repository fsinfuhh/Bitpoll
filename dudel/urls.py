"""dudel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponseServerError
from django.shortcuts import redirect
import django.conf.urls.i18n
from django.template import Context, loader

from dudel import settings

urlpatterns = [
    url(r'^poll/', include('dudel.poll.urls')),
    url(r'^', include('dudel.base.urls')),
    url(r'^invitations/', include('dudel.invitations.urls')),
    url(r'^$', lambda req: redirect('index'), name='home'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login', ),
    url(r'^logout/$', auth_views.logout, {
        'next_page': '/'
    }, name='logout'),
    url('^markdown/', include('django_markdown.urls')),
    url(r'^registration/', include('dudel.registration.urls')),

    url(r'^i18n/', include(django.conf.urls.i18n)),
    url(r'^admin/', admin.site.urls),

]


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """

    t = loader.get_template('500.html')  # You need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'request': request,
    })))


"""
    url(r'^register$', views.index, name='index'),
    url(r'^user/language$', views.index, name='index'),
    url(r'^groups$', views.index, name='index'),
    url(r'^groups/(\d+)$', views.index, name='index'),
    url(r'^groups/(\d+)/disband$', views.index, name='index'),
    url(r'^groups/(\d+)/make-admin/(\d+)$', views.index, name='index'),
    url(r'^groups/(\d+)/leave/(\d+)$', views.index, name='index'),
    url(r'^user/settings$', views.index, name='index'),
    url(r'^api/members$', views.getMembers, name='poll_getMembers'),"""
