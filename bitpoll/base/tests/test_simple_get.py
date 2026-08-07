import pytest

from bitpoll.tests._base import get_dynamic_url, get_module_urls


pytestmark = pytest.mark.django_db

URLS = get_module_urls("base")


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_without_login(client, url_name, arg_count):
    response = client.get(get_dynamic_url([], url_name))
    match url_name:
        case "settings" | "base_autocomplete":
            assert response.status_code == 302
        case _:
            assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_with_login(client, django_user_model, url_name, arg_count):
    user = django_user_model.objects.create_user(username="base-user", password="password")
    client.force_login(user)
    response = client.get(get_dynamic_url([], url_name))
    assert response.status_code == 200


