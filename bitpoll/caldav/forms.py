from django.conf import settings
from django.forms import ModelForm, CharField, PasswordInput, forms
from django_token_bucket.models import TokenBucket
from .models import DavCalendar
from django.utils.translation import ugettext as _


class DavCalendarForm(ModelForm):
    user = CharField(required=False)
    password = CharField(widget=PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        self.db_user = kwargs.pop('user')
        super(DavCalendarForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DavCalendar
        fields = [
            'url',
            'name',
        ]

    def clean(self):
        cleaned_data = super(DavCalendarForm, self).clean()
        bucket = TokenBucket.get(identifier='calendars_added',
                                 user=self.db_user,
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
