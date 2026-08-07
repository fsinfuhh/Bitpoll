import pytest
from model_bakery import baker
from django.core import signing
from django.urls import reverse

from bitpoll.base.models import BitpollUser


pytestmark = pytest.mark.django_db


def test_request_account_post_sends_activation_email(client):
    data = {
        "username": "new-registration-user",
        "first_name": "New",
        "last_name": "User",
        "email": "new-user@example.com",
        "auto_watch": "",
        "email_invitation": "on",
    }

    response = client.post(reverse("registration_request_account"), data)

    assert response.status_code == 302
    assert response.url.endswith("/new-user@example.com")


def test_create_account_post_creates_user(client):
    token = signing.dumps(
        {
            "username": "created-user",
            "first_name": "Created",
            "last_name": "User",
            "email": "created@example.com",
            "email_invitation": True,
        }
    )

    response = client.post(
        reverse("registration_create_account", args=[token]),
        {"new_password1": "SafePassword123!", "new_password2": "SafePassword123!"},
    )

    assert response.status_code == 302
    user = BitpollUser.objects.get(username="created-user")
    assert user.check_password("SafePassword123!")


def test_account_nickname_post_updates_user(client):
    user = baker.make("base.BitpollUser", _fill_optional=True, username="nickname-user")
    client.force_login(user)

    response = client.post(
        reverse("registration_account"),
        {"form": "change_nick", "nickname": "New Nickname"},
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.displayname == "New Nickname (nickname-user)"

