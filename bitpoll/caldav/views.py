from urllib.parse import urlparse, urlencode

from caldav import DAVClient, Calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from urllib3.util import parse_url, Url

from bitpoll.caldav.models import DavCalendar
from .forms import DavCalendarForm


@require_POST
@login_required
def change_callendar(request):
    form = DavCalendarForm(request.POST)
    if form.is_valid():
        # todo ratelimiting (code in dashboard?)
        caldav_obj = form.save(commit=False)
        user = urlencode(form.cleaned_data['user'])
        passwd = urlencode(form.cleaned_data['password'])
        auth = user
        if passwd:
            auth += ':'
            auth += passwd
        parsed = parse_url(caldav_obj.url)
        if auth:
            parsed = Url(
                scheme=parsed.scheme,
                auth=auth,
                host=parsed.host,
                port=parsed.port,
                path=parsed.path,
                query=parsed.query,
                fragment=parsed.fragment
            )
        if parsed.scheme.startswith('http'):
            try:
                calendar = Calendar(client=DAVClient(parsed.url),
                                    url=parsed.url)
                calendar.date_search(now(), now())
                caldav_obj.url = parsed.url
                caldav_obj.user = request.user
                caldav_obj.save()
                return redirect('settings')
            except Exception as e:
                form.add_error(None, str(e))
    elif 'delete' in request.POST:
        obj = get_object_or_404(DavCalendar, id=request.POST['delete'])
        obj.delete()
        return redirect('settings')
    #todo: extract user/password from url?
    return TemplateResponse(request, "caldav/caldav.html", {
        'calendar_form': form,
        'calendars': DavCalendar.objects.filter(user=request.user),
    })
