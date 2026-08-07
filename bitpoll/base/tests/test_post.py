import pytest
from model_bakery import baker
from django.forms.models import model_to_dict
from django.urls import reverse

from bitpoll.base.models import BitpollUser
from bitpoll.poll.models import ChoiceValue, Poll, PollWatch, Vote


pytestmark = pytest.mark.django_db


def test_poll_creation_post_creates_poll_and_values(client):
    user = baker.make("base.BitpollUser", _fill_optional=True, username="poll-creator")
    client.force_login(user)
    data = {
        "title": "Created poll",
        "type": "universal",
        "public_listening": "",
        "due_date": "",
        "url": "created-poll",
        "description": "Created through POST",
        "anonymous_allowed": "on",
        "require_login": "",
        "require_invitation": "",
        "allow_unauthenticated_vote_changes": "on",
        "one_vote_per_user": "on",
        "vote_all": "",
    }

    response = client.post(reverse("index"), data)

    assert response.status_code == 302
    poll = Poll.objects.get(url="created-poll")
    assert poll.user == user
    assert ChoiceValue.objects.filter(poll=poll).count() == 4


def test_user_settings_post_updates_user_and_watch(client):
    user = baker.make("base.BitpollUser", _fill_optional=True, username="settings-user")
    poll = baker.make(Poll, _fill_optional=True, user=user, url="settings-poll", due_date=None)
    baker.make(Vote, _fill_optional=True, poll=poll, user=user)
    client.force_login(user)
    data = model_to_dict(user, fields=["auto_watch", "email_invitation", "timezone", "language"])
    data.update({"auto_watch": True, "email_invitation": False, "timezone": "UTC", "language": "english"})

    response = client.post(reverse("settings"), data)

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.auto_watch is True
    assert user.timezone == "UTC"
    assert PollWatch.objects.filter(poll=poll, user=user).exists()



