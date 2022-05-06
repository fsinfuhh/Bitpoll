from caldav import Calendar as DavCalendar, DAVClient
from caldav.lib.error import AuthorizationError
from django.conf import settings
from django.core.cache import cache
from django.contrib import messages
from django.utils.translation import gettext_lazy
from icalendar import Calendar
from typing import List

from bitpoll.base.models import BitpollUser
from bitpoll.poll.models import Choice, Poll


def get_caldav(choices: List[Choice], current_poll: Poll, user: BitpollUser, request):
    # calendar stuff
    events2 = []
    if not settings.CALENDAR_ENABLED or not (user.is_authenticated and current_poll.type == 'datetime' and choices):
        for choice in choices:
            events2.append([])
        return events2
    start = choices[0].date
    end = choices[-1].date

    # experimental: fetch calendar(s)
    events = []
    for calendar_obj in user.davcalendar_set.all():
        cache_key = "calendar_{}_events_{}-{}".format(calendar_obj.id, start, end).replace(' ', '_')
        events_calendar = cache.get(cache_key)
        if events_calendar is None:
            events_calendar = []
            try:
                calendar = DavCalendar(client=DAVClient(calendar_obj.url),
                                       url=calendar_obj.url)
                appointments = calendar.date_search(start, end)
                for appointment in appointments:
                    ical = Calendar.from_ical(appointment.data)
                    for event in ical.walk():
                        if event.name == "VEVENT":
                            try:
                                if "DTEND" in event:
                                    end = event.decoded('DTEND')
                                else:
                                    duration = event.decoded("DURATION")
                                    if isinstance(duration, list):
                                        duration = duration[0]  # todo: use all elements?? what does it mean if there are more than one element?
                                    end = event.decoded('DTSTART') + duration
                                events_calendar.append({
                                    "DTSTART": event.decoded('DTSTART'),
                                    "DTEND": end,
                                    "NAME": event.get('summary').title(),
                                })
                            except (AttributeError, ValueError, TypeError) as e:
                                # we ignore the event we can not parse, but send it to sentry
                                try:
                                    from sentry_sdk import capture_exception
                                    capture_exception(e)
                                except Exception:
                                    # if the sending of the error does fail we ignore it
                                    pass
                cache.set(cache_key, events_calendar)
            except AuthorizationError as e:
                messages.warning(request, ugettext_lazy('Could not access your calendar "%s" due to an authorization error' % calendar_obj.name))
        events += events_calendar
    for choice in choices:
        ev_tmp = []
        for event in events:
            if isinstance(event['DTSTART'], type(choice.date)):
                # datetime
                if event['DTSTART'] <= choice.date and event['DTEND'] >= choice.date:
                    ev_tmp.append(event)
            else:
                # dates
                if event['DTSTART'] <= choice.date.date() <= event['DTEND']:
                    ev_tmp.append(event)
        events2.append(ev_tmp)
    return events2
