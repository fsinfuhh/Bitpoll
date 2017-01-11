from enum import Enum

from django.utils.formats import date_format


class DateTimePart(str, Enum):
    date = "date"
    time = "time"
    datetime = "datetime"


class PartialDateTime(object):
    def __init__(self, datetime, part):
        self.datetime = datetime
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
