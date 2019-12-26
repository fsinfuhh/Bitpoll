from datetime import timedelta
from urllib.parse import quote_plus

from caldav import DAVClient, Calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy
from django.views.decorators.http import require_POST
from urllib3.util import parse_url, Url

from bitpoll.caldav.models import DavCalendar
from .forms import DavCalendarForm


@require_POST
@login_required
def change_calendar(request):
    form = DavCalendarForm(request.POST, user=request.user)
    if form.is_valid():
        caldav_obj = form.save(commit=False)
        user = quote_plus(form.cleaned_data['user'])
        passwd = quote_plus(form.cleaned_data['password'])
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
        if parsed.scheme in ('http', 'https'):
            old_calendars = DavCalendar.objects.filter(user=request.user)
            exists = False
            # This is necessary as the urls are encrypted in the DB and can't filtered wherefore
            for old_calendar in old_calendars:
                if old_calendar.url == parsed.url:
                    exists = True
                    break
            if not exists:
                try:
                    calendar = Calendar(client=DAVClient(parsed.url),
                                        url=parsed.url)
                    calendar.date_search(now(), now() + timedelta(hours=1))
                    caldav_obj.url = parsed.url
                    caldav_obj.user = request.user
                    caldav_obj.save()
                    return redirect('settings')
                except Exception as e:
                    form.add_error(None, ugettext_lazy("Error getting Calendar: {}".format(str(e))))
            else:
                form.add_error(None, ugettext_lazy("This calendar is already configured"))
        else:
            form.add_error('url', ugettext_lazy("The URL should start with http:// or https://"))
    elif 'delete' in request.POST:
        obj = get_object_or_404(DavCalendar, id=request.POST['delete'], user=request.user)
        obj.delete()
        return redirect('settings')
    # todo: extract user/password from url?
    return TemplateResponse(request, "caldav/caldav.html", {
        'calendar_form': form,
        'calendars': DavCalendar.objects.filter(user=request.user),
    })
