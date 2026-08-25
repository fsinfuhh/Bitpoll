import pytest

from bitpoll.caldav.models import DavCalendar
from bitpoll.tests._base import get_dynamic_url, get_module_urls


URLS = get_module_urls("caldav")


@pytest.fixture
def calendar_data(db, django_user_model, settings):
    settings.FIELD_ENCRYPTION_KEY = "this+is+an+example+key+please+generate+one+="
    user = django_user_model.objects.create_user(username="caldav-user", password="password")
    calendar = DavCalendar.objects.create(user=user, url="https://calendar.example/", name="Test calendar")
    return user, calendar


def url_args(url_name, calendar):
    return [calendar.pk] if "edit" in url_name else []


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_without_login(client, calendar_data, url_name, arg_count):
    _, calendar = calendar_data
    response = client.get(get_dynamic_url(url_args(url_name, calendar), url_name))
    match url_name:
        case "change_calendar" | "edit_save_calendar":
            assert response.status_code == 405
        case "edit_calendar":
            assert response.status_code == 302
        case _:
            assert response.status_code == 200


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_with_login(client, calendar_data, url_name, arg_count):
    user, calendar = calendar_data
    client.force_login(user)
    response = client.get(get_dynamic_url(url_args(url_name, calendar), url_name))
    match url_name:
        case "change_calendar" | "edit_save_calendar":
            assert response.status_code == 405
        case _:
            assert response.status_code == 200

