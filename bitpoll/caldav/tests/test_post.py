import pytest
from model_bakery import baker
from django.urls import reverse

from bitpoll.caldav.models import DavCalendar


pytestmark = pytest.mark.django_db


@pytest.fixture
def calendar_data(settings):
    settings.FIELD_ENCRYPTION_KEY = "this+is+an+example+key+please+generate+one+="
    user = baker.make("base.BitpollUser", _fill_optional=True, username="caldav-user")
    calendar = baker.make(
        DavCalendar,
        _fill_optional=True,
        user=user,
        url="https://calendar.example/",
        name="Test calendar",
    )
    return user, calendar


def test_delete_calendar_post_deletes_calendar(client, calendar_data):
    user, calendar = calendar_data
    client.force_login(user)

    response = client.post(
        reverse("change_calendar"),
        {"delete": str(calendar.pk)},
    )

    assert response.status_code == 302
    assert not DavCalendar.objects.filter(pk=calendar.pk).exists()


def test_create_calendar_post_saves_calendar(client, calendar_data, monkeypatch):
    user, _ = calendar_data
    client.force_login(user)

    class FakeCalendar:
        def __init__(self, **kwargs):
            pass

        def date_search(self, *args):
            return []

    monkeypatch.setattr("bitpoll.caldav.views.Calendar", FakeCalendar)
    monkeypatch.setattr("bitpoll.caldav.views.DAVClient", lambda url: object())

    response = client.post(
        reverse("change_calendar"),
        {
            "url_0": "https://new-calendar.example/",
            "url_1": "",
            "url_2": "",
            "name": "New calendar",
        },
    )

    assert response.status_code == 302
    assert DavCalendar.objects.filter(user=user, name="New calendar").exists()


