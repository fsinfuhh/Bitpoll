from datetime import timedelta

from caldav import DAVClient, Calendar
from caldav.lib.error import AuthorizationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy
from django.views.decorators.http import require_POST
from urllib3.util import parse_url

from bitpoll.caldav.models import DavCalendar
from .forms import DavCalendarForm


@require_POST
@login_required
def change_calendar(request, calendar_id: int = None):
    if calendar_id:
        calendar = get_object_or_404(DavCalendar, id=calendar_id, user=request.user)
        form = DavCalendarForm(request.POST, instance=calendar, user=request.user)
    else:
        form = DavCalendarForm(request.POST, user=request.user)
    if form.is_valid():
        caldav_obj = form.save(commit=False)
        old_calendars = DavCalendar.objects.filter(user=request.user).exclude(id=calendar_id)
        exists = False
        # This is necessary as the urls are encrypted in the DB and can't filtered wherefore
        for old_calendar in old_calendars:
            if old_calendar.id != calendar_id and old_calendar.url == caldav_obj.url:
                exists = True
                break
        if not exists:
            try:
                calendar = Calendar(client=DAVClient(caldav_obj.url),
                                    url=caldav_obj.url)
                calendar.date_search(now(), now() + timedelta(hours=1))
                caldav_obj.user = request.user
                caldav_obj.save()
                return redirect('settings')
            except AuthorizationError as e:
                form.add_error(None, ugettext_lazy(
                    "Error getting Calendar {}: Authorization Required".format(caldav_obj.url)))
            except Exception as e:
                form.add_error(None, gettext_lazy("Error getting Calendar: {}".format(str(e))))
        else:
            form.add_error(None, gettext_lazy("This calendar is already configured"))
    elif 'delete' in request.POST:
        obj = get_object_or_404(DavCalendar, id=request.POST['delete'], user=request.user)
        obj.delete()
        messages.success(request, ugettext_lazy("Calendar Deleted"))
        return redirect('settings')
    return TemplateResponse(request, "caldav/caldav.html", {
        'calendar_form': form,
        'calendars': DavCalendar.objects.filter(user=request.user),
        'calendar_id': calendar_id,
        'edit': calendar_id is not None,
    })


@login_required
def edit_calendar(request, calendar_id: int):
    calendar = get_object_or_404(DavCalendar, id=calendar_id, user=request.user)
    form = DavCalendarForm(instance=calendar, user=request.user)
    return TemplateResponse(request, "caldav/caldav.html", {
        'calendar_form': form,
        'edit': True,
        'calendar_id': calendar_id,
    })


@login_required
def delete_calendar_confirm(request, calendar_id: int):
    calendar = get_object_or_404(DavCalendar, id=calendar_id, user=request.user)
    url_parsed = parse_url(calendar.url)
    # remove the auth from the url
    url = "{}://{}{}{}".format(url_parsed.scheme, url_parsed.host,
                               ":{}".format(url_parsed.port) if url_parsed.port else "", url_parsed.request_uri)
    return TemplateResponse(request, "caldav/delete_confirm.html", {
        'calendar_id': calendar_id,
        'calendar_name': calendar.name,
        'calendar_url': url,
    })
