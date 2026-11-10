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


def test_logout_get_is_not_allowed(client, django_user_model):
    # Since Django 5 LogoutView only accepts POST requests.
    user = django_user_model.objects.create_user(username="logout-get", password="password")
    client.force_login(user)

    response = client.get(reverse("logout"))

    assert response.status_code == 405


def test_logout_post_logs_user_out(client, django_user_model):
    user = django_user_model.objects.create_user(username="logout-post", password="password")
    client.force_login(user)

    response = client.post(reverse("logout"))

    assert response.status_code == 302
    assert response["Location"] == reverse("index")
    assert "_auth_user_id" not in client.session


def test_logout_is_rendered_as_post_form(client, django_user_model):
    # A plain link to /logout/ would trigger the 405 from LogoutView, so the
    # navigation must submit a POST form instead.
    user = django_user_model.objects.create_user(username="logout-form", password="password")
    client.force_login(user)

    response = client.get(reverse("index"))

    assert response.status_code == 200
    content = response.content.decode()
    assert f'<form method="post" action="{reverse("logout")}">' in content
    assert f'<a href="{reverse("logout")}">' not in content
