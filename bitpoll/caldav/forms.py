from urllib.parse import quote_plus, urlparse, urlsplit, urlunsplit

from django.conf import settings
from django.core.validators import URLValidator
from django.forms import ModelForm, CharField, PasswordInput, forms, MultiValueField, URLField, MultiWidget, URLInput, \
    TextInput
from django.utils.translation import ugettext as _
from urllib3.util import Url, parse_url

from django_token_bucket.models import TokenBucket
from .models import DavCalendar
from bitpoll.base.models import BitpollUser


class URLAuthWidget(MultiWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes.
    """

    def __init__(self):
        widgets = (
            URLInput(
            ),
            TextInput(
            ),
            PasswordInput(
            )
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            parsed = urlsplit(value)
            scheme, netloc, path, query, fragment = parsed
            user = parsed.username
            passwd = parsed.password
            host = parsed.hostname
            port = parsed.port
            url = ""

            if scheme != "":
                url += scheme + "://"
            if host is not None:
                url += host
            if port is not None:
                url += ":" + str(port)
            if path != "":
                url += path
            if query != "":
                url += u"?" + query
            if fragment != "":
                url += "#" + fragment
            return [url, user, passwd]
        return [None, None, None]


class URLAuthField(MultiValueField):
    widget = URLAuthWidget

    def __init__(self, **kwargs):
        max_lengh = kwargs.pop('max_length')  # TODO use this in validation of the whole field
        required = kwargs.pop('required')  # TODO use this in validation of the whole field
        fields = (
            URLField(validators=[URLValidator(schemes=['http', 'https'])], help_text="URL", required=True),
            CharField(required=False, help_text="User"),
            CharField(required=False, help_text="Password", widget=PasswordInput),
        )
        super().__init__(
            # error_messages=error_messages,
            fields=fields,
            require_all_fields=False, **kwargs
        )

    def compress(self, data_list):
        user = quote_plus(data_list[1])
        passwd = quote_plus(data_list[2])
        auth = user
        if passwd:
            auth += ':'
            auth += passwd
        parsed = urlsplit(data_list[0])
        if auth:
            host = auth + '@' + parsed.netloc
            return urlunsplit((
                parsed.scheme,
                host,
                parsed.path,
                parsed.query,
                parsed.fragment
            ))
        return parsed.url


class DavCalendarForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.db_user: BitpollUser = kwargs.pop('user')
        super(DavCalendarForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DavCalendar
        fields = [
            'url',
            'name',
        ]
        field_classes = {
            'url': URLAuthField
        }

    def clean(self):
        cleaned_data = super(DavCalendarForm, self).clean()
        bucket = TokenBucket.get(identifier='calendars_added',
                                 ref_object=self.db_user,
                                 max_tokens=settings.CALENDAR_MAX_TOKENS,  # TODO: better name
                                 fill_rate=settings.CALENDAR_FILL_RATE,
                                 whatfor=_('adding Calendars'))
        try:
            bucket.consume(1)
        except bucket.TokensExceeded as e:
            raise forms.ValidationError(e.get_message(self.db_user.timezone))
        if DavCalendar.objects.filter(user=self.db_user).count() > 10:
            raise forms.ValidationError("Maximum count of calendars reached (10)")
        return cleaned_data
