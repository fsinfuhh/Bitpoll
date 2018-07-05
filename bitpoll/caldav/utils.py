from caldav import Calendar as DavCalendar, DAVClient
from icalendar import Calendar
from typing import List

from bitpoll.base.models import BitpollUser
from bitpoll.poll.models import Choice, Poll


def get_caldav(choices: List[Choice ], current_poll: Poll, user: BitpollUser):
    # calendar stuff
    events2 = []
    if current_poll.type == 'datetime':
        start = choices[0].date
        end = choices[-1].date

        # experimental: fetch calendar(s)
        events = []
        for calendar_obj in user.davcalendar_set.all():
            calendar = DavCalendar(client=DAVClient(calendar_obj.url),
                                   url=calendar_obj.url)  # Todo: beides gleiche url? beim login im DAVClient eine andere??
            # Todo: eventuell doch via client.principal() iterieren?
            appointments = calendar.date_search(start, end)
            calendar = Calendar()
            for appointment in appointments:
                ical = calendar.from_ical(appointment.data)
                print(ical)
                for event in ical.walk():
                    if event.name == "VEVENT":
                        events.append({
                            "DTSTART": event.get('DTSTART').dt,
                            "DTEND": event.get('DTEND').dt,
                            "NAME": event.get('summary').title(),
                        })
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