from urllib.parse import quote_plus

from django.conf import settings
from django.core.validators import URLValidator
from django.forms import ModelForm, CharField, PasswordInput, forms, MultiValueField, URLField, MultiWidget, URLInput, \
    TextInput
from django.utils.translation import ugettext as _
from urllib3.util import Url, parse_url

from django_token_bucket.models import TokenBucket
from .models import DavCalendar


class URLAuthWidget(MultiWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes.
    """
    template_name = 'caldav/url_auth.html'

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
            parsed = parse_url(value)
            scheme, auth, host, port, path, query, fragment = parsed
            url = u""
            user = None
            passwd = None

            # We use "is not None" we want things to happen with empty strings (or 0 port)
            if scheme is not None:
                url += scheme + u"://"
            if auth is not None:
                user = auth.split(':')[0]
                if ":" in auth:
                    passwd = auth.split(':')[1]
            if host is not None:
                url += host
            if port is not None:
                url += u":" + str(port)
            if path is not None:
                url += path
            if query is not None:
                url += u"?" + query
            if fragment is not None:
                url += u"#" + fragment
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
        parsed = parse_url(data_list[0])
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
        return parsed.url


class DavCalendarForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.db_user = kwargs.pop('user')
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
            raise forms.ValidationError(str(e))
        if DavCalendar.objects.filter(user=self.db_user).count() > 10:
            raise forms.ValidationError("Maximum count of calendars reached (10)")
        return cleaned_data
