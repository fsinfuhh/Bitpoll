import pytest

from bitpoll.tests._base import get_dynamic_url, get_module_urls


URLS = get_module_urls("registration")


def url_args(url_name):
    if "successful" in url_name:
        return ["user@example.com"]
    if "change_email" in url_name or "create_account" in url_name:
        return ["invalid-token"]
    if "confirm" in url_name:
        return ["1", "invalid-token"]
    return []


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_without_login(client, url_name, arg_count):
    response = client.get(get_dynamic_url(url_args(url_name), url_name))
    match url_name:
        case "registration_change_email" | "registration_account":
            assert response.status_code == 302
        case _:
            assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_with_login(client, django_user_model, url_name, arg_count):
    user = django_user_model.objects.create_user(username="registration-user", password="password")
    client.force_login(user)
    response = client.get(get_dynamic_url(url_args(url_name), url_name))
    match url_name:
        case "registration_create_account":
            assert response.status_code == 302
        case _:
            assert response.status_code == 200

