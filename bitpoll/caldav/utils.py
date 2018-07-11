from caldav import Calendar as DavCalendar, DAVClient
from django.core.cache import cache
from icalendar import Calendar
from typing import List

from bitpoll.base.models import BitpollUser
from bitpoll.poll.models import Choice, Poll


def get_caldav(choices: List[Choice], current_poll: Poll, user: BitpollUser):
    # calendar stuff
    events2 = []
    if current_poll.type == 'datetime':
        start = choices[0].date
        end = choices[-1].date

        # experimental: fetch calendar(s)
        events = []
        for calendar_obj in user.davcalendar_set.all():
            cache_key = "calendar_{}_events_{}-{}".format(calendar_obj.id, start, end).replace(' ', '_')
            events_calendar = cache.get(cache_key)
            if events_calendar is None:
                print("not chached")
                events_calendar = []
                calendar = DavCalendar(client=DAVClient(calendar_obj.url),
                                       url=calendar_obj.url)
                appointments = calendar.date_search(start, end)
                calendar = Calendar()
                for appointment in appointments:
                    ical = calendar.from_ical(appointment.data)
                    for event in ical.walk():
                        if event.name == "VEVENT":
                            events_calendar.append({
                                "DTSTART": event.get('DTSTART').dt,
                                "DTEND": event.get('DTEND').dt,
                                "NAME": event.get('summary').title(),
                            })
                cache.set(cache_key, events_calendar)
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