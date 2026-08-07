import pytest

from bitpoll.invitations.models import Invitation
from bitpoll.poll.models import Poll
from bitpoll.tests._base import get_dynamic_url, get_module_urls


URLS = get_module_urls("invitations")


@pytest.fixture
def invitation_data(db, django_user_model):
    user = django_user_model.objects.create_user(username="invitation-user", password="password")
    poll = Poll.objects.create(title="Invitation poll", url="invitation-poll", type="universal", user=user)
    invitation = Invitation.objects.create(
        date_created="2026-01-01T12:00:00Z", creator=user, user=user, poll=poll
    )
    return user, poll, invitation


def url_args(poll):
    return [poll.url]


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_without_login(client, invitation_data, url_name, arg_count):
    _, poll, _ = invitation_data
    response = client.get(get_dynamic_url(url_args(poll), url_name))
    match url_name:
        case "invitations_send":
            assert response.status_code == 405
        case _:
            assert response.status_code == 200


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_with_login(client, invitation_data, url_name, arg_count):
    user, poll, _ = invitation_data
    client.force_login(user)
    response = client.get(get_dynamic_url(url_args(poll), url_name))
    match url_name:
        case "invitations_send":
            assert response.status_code == 405
        case _:
            assert response.status_code == 200

