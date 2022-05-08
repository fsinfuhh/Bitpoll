from enum import Enum

from django.utils.formats import date_format
from django.utils.timezone import localtime


class DateTimePart(str, Enum):
    date = "date"
    time = "time"
    datetime = "datetime"


class PartialDateTime(object):
    def __init__(self, datetime, part, tz):
        self.datetime = localtime(datetime, tz)
        self.part = part

    def __lt__(self, other):
        return self.datetime < other.datetime

    def __eq__(self, other):
        return isinstance(other, PartialDateTime) and self.part == other.part and self.format() == other.format()

    def format(self):
        if self.part == DateTimePart.date:
            return date_format(self.datetime, format='D, j. N Y')
        elif self.part == DateTimePart.time:
            return date_format(self.datetime, format='H:i')
        elif self.part == DateTimePart.datetime:
            return date_format(self.datetime, format='D, j. N Y H:i')


#From: https://stackoverflow.com/questions/18092354/python-split-string-without-splitting-escaped-character
def split_unescape(s, delim, escape='\\', unescape=True):
    """
    >>> split_unescape('foo,bar', ',')
    ['foo', 'bar']
    >>> split_unescape('foo$,bar', ',', '$')
    ['foo,bar']
    >>> split_unescape('foo$$,bar', ',', '$', unescape=True)
    ['foo$', 'bar']
    >>> split_unescape('foo$$,bar', ',', '$', unescape=False)
    ['foo$$', 'bar']
    >>> split_unescape('foo$', ',', '$', unescape=True)
    ['foo$']
    """
    ret = []
    current = []
    itr = iter(s)
    for ch in itr:
        if ch == escape:
            try:
                # skip the next character; it has been escaped!
                if not unescape:
                    current.append(escape)
                current.append(next(itr))
            except StopIteration:
                if unescape:
                    current.append(escape)
        elif ch == delim:
            # split! (add current to the list and reset it)
            ret.append(''.join(current))
            current = []
        else:
            current.append(ch)
    ret.append(''.join(current))
    return ret
