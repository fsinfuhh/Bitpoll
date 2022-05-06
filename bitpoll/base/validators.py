from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from pytz import all_timezones


def validate_timezone(value):
    if value not in all_timezones:
        raise ValidationError(
            _('%(value)s is not a valid timezone'),
            params={'value': value},
        )
