import pytest
from faker import Faker
from model_bakery import baker
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils.timezone import now

from bitpoll.poll.models import Choice, ChoiceValue, Comment, Poll, PollWatch, Vote, VoteChoice


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return baker.make(
        "base.BitpollUser",
        _fill_optional=True,
        username="poll-owner",
        password="password",
        is_active=True,
    )


@pytest.fixture
def user():
    return baker.make(
        "base.BitpollUser",
        _fill_optional=True,
        username="poll-user",
        password="password",
        is_active=True,
    )


@pytest.fixture
def poll(owner):
    return baker.make(
        Poll,
        _fill_optional=True,
        title="Test poll",
        url="test-poll",
        type="universal",
        user=owner,
        anonymous_allowed=True,
        require_login=False,
        require_invitation=False,
        allow_unauthenticated_vote_changes=True,
        one_vote_per_user=True,
        vote_all=False,
        due_date=None,
    )


@pytest.fixture
def choice(poll):
    return baker.make(
        Choice,
        _fill_optional=True,
        poll=poll,
        text="Original choice",
        sort_key=0,
        deleted=False,
    )


@pytest.fixture
def value(poll):
    return baker.make(
        ChoiceValue,
        _fill_optional=True,
        poll=poll,
        title="Yes",
        icon="check",
        color="00ff00",
        deleted=False,
    )


def post_url(name, poll, *args):
    return reverse(name, args=[poll.url, *args])


def test_comment_post_creates_comment(client, poll, user):
    client.force_login(user)
    comment = baker.make(Comment, _fill_optional=True, poll=poll, user=user)
    data = model_to_dict(comment, fields=["name", "text"])
    data["text"] = "A new comment"

    response = client.post(post_url("poll_comment", poll), data)

    assert response.status_code == 302
    comment = Comment.objects.exclude(pk=comment.pk).get(poll=poll)
    assert comment.text == "A new comment"
    assert comment.user == user
    assert comment.name == user.get_displayname()


def test_comment_edit_post_updates_comment(client, poll, user):
    comment = baker.make(Comment, _fill_optional=True, poll=poll, user=user, text="Old")
    client.force_login(user)
    data = model_to_dict(comment, fields=["name", "text"])
    data["text"] = Faker().sentence()

    response = client.post(post_url("poll_comment_edit", poll, comment.pk), data)

    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == data["text"]


def test_watch_post_toggles_watch(client, poll, user):
    client.force_login(user)
    url = post_url("poll_watch", poll)

    assert client.post(url).status_code == 302
    assert PollWatch.objects.filter(poll=poll, user=user).exists()

    assert client.post(url).status_code == 302
    assert not PollWatch.objects.filter(poll=poll, user=user).exists()


def test_universal_choice_post_creates_and_updates_choices(client, poll, choice):
    client.force_login(poll.user)
    data = {
        "choice_text": ["Changed choice", "New choice"],
        "choice_sort_key": [str(choice.pk), "1"],
        **{
            f"choice_text_{choice.pk}": model_to_dict(choice)["text"],
            f"choice_sort_key_{choice.pk}": str(choice.sort_key),
        },
        "next": "Poll",
    }
    data[f"choice_text_{choice.pk}"] = Faker().sentence()[:80]

    response = client.post(post_url("poll_editUniversalChoice", poll), data)

    assert response.status_code == 302
    choice.refresh_from_db()
    assert choice.text == data[f"choice_text_{choice.pk}"]
    assert Choice.objects.filter(poll=poll, text="New choice", deleted=False).exists()


def test_universal_choice_post_soft_deletes_choice(client, poll, choice):
    client.force_login(poll.user)

    response = client.post(
        post_url("poll_editUniversalChoice", poll),
        {f"choice_text_{choice.pk}": "", "delete": str(choice.pk)},
    )

    assert response.status_code == 200
    choice.refresh_from_db()
    assert choice.deleted is True


def test_date_choice_post_replaces_choices(client, owner):
    poll = baker.make(Poll, user=owner, type="date", url="date-poll")
    old_choice = baker.make(Choice, poll=poll, date=now(), text="", sort_key=0)
    client.force_login(owner)

    response = client.post(
        post_url("poll_editDateChoice", poll),
        {"dates": "2026-08-10,2026-08-11"},
    )

    assert response.status_code == 302
    old_choice.refresh_from_db()
    assert old_choice.deleted is True
    assert Choice.objects.filter(poll=poll, deleted=False).count() == 2


def test_datetime_combinations_post_creates_choices(client, owner):
    poll = baker.make(Poll, user=owner, type="datetime", url="datetime-poll")
    client.force_login(owner)

    response = client.post(
        post_url("poll_editDTChoiceCombinations", poll),
        {"datetimes[]": ["2026-08-10 10:00", "2026-08-10 11:00"]},
    )

    assert response.status_code == 302
    assert Choice.objects.filter(poll=poll, deleted=False).count() == 2


def test_choice_value_create_post_creates_value(client, poll):
    client.force_login(poll.user)
    choice_value = baker.make(ChoiceValue, _fill_optional=True, poll=poll)
    data = model_to_dict(choice_value, fields=["title", "icon", "color", "weight"])
    data.update(title="Maybe", color="#abcdef")

    response = client.post(post_url("poll_editchoicevalues_create", poll), data)

    assert response.status_code == 302
    created = ChoiceValue.objects.get(poll=poll, title="Maybe")
    assert created.color == "abcdef"


def test_vote_post_creates_vote_and_votechoice(client, poll, choice, value):
    vote = baker.make(Vote, _fill_optional=True, poll=poll)
    data = model_to_dict(vote, fields=["comment"])
    vote.delete()
    data.update(
        {
            str(choice.pk): str(value.pk),
            f"comment_{choice.pk}": "Vote comment",
            "name": "",
            "anonymous": "true",
        }
    )
    data["comment"] = ""

    response = client.post(post_url("poll_vote", poll), data)

    assert response.status_code == 302
    vote = Vote.objects.get(poll=poll)
    assert vote.user is None
    assert vote.anonymous is True
    assert VoteChoice.objects.filter(vote=vote, choice=choice, value=value, comment="Vote comment").exists()


def test_vote_edit_post_replaces_votechoices(client, poll, choice, value, user):
    vote = baker.make(Vote, _fill_optional=True, poll=poll, user=user, comment="Old")
    old_choice = baker.make(Choice, _fill_optional=True, poll=poll, sort_key=1)
    old_value = baker.make(ChoiceValue, _fill_optional=True, poll=poll)
    baker.make(
        VoteChoice,
        _fill_optional=True,
        vote=vote,
        choice=old_choice,
        value=old_value,
    )
    client.force_login(user)
    data = model_to_dict(vote, fields=["comment"])
    data.update({"vote_id": str(vote.pk), str(choice.pk): str(value.pk), f"comment_{choice.pk}": "New choice comment"})

    data["comment"] = Faker().sentence()
    response = client.post(post_url("poll_voteEdit", poll, vote.pk), data)

    assert response.status_code == 302
    vote.refresh_from_db()
    assert vote.comment == data["comment"]
    assert VoteChoice.objects.filter(vote=vote, choice=choice, value=value).exists()
    assert not VoteChoice.objects.filter(vote=vote, choice=old_choice).exists()


def test_vote_assign_post_assigns_user(client, poll, owner, user):
    vote = baker.make(Vote, _fill_optional=True, poll=poll, name="Anonymous")
    client.force_login(owner)

    response = client.post(post_url("poll_voteAssign", poll, vote.pk), {"username": user.username})

    assert response.status_code == 302
    vote.refresh_from_db()
    assert vote.user == user
    assert vote.assigned_by == owner


def test_vote_delete_post_deletes_vote(client, poll, user):
    vote = baker.make(Vote, _fill_optional=True, poll=poll, user=user)
    client.force_login(user)

    response = client.post(post_url("poll_voteDelete", poll, vote.pk), {"Delete": "Delete"})

    assert response.status_code == 302
    assert not Vote.objects.filter(pk=vote.pk).exists()


def test_settings_post_updates_poll(client, poll):
    client.force_login(poll.user)
    data = {
        "title": "Updated title",
        "due_date": "",
        "show_results": "summary",
        "timezone_name": "UTC",
        "description": "Updated description",
        "allow_comments": "on",
        "anonymous_allowed": "on",
        "require_login": "",
        "require_invitation": "",
        "allow_unauthenticated_vote_changes": "on",
        "one_vote_per_user": "on",
        "show_invitations": "on",
        "group": "",
        "public_listening": "",
        "vote_all": "",
        "hide_participants": "",
        "use_user_timezone": "",
        "sorting": "0",
        "show_score_in_summary": "",
        "user": poll.user.username,
    }

    response = client.post(post_url("poll_settings", poll), data)

    assert response.status_code == 302
    poll.refresh_from_db()
    assert poll.title == "Updated title"
    assert poll.show_results == "summary"
    assert poll.timezone_name == "UTC"


def test_copy_post_copies_choices_and_values(client, poll, choice, value):
    client.force_login(poll.user)

    response = client.post(
        post_url("poll_copy", poll),
        {
            "title": "Copied poll",
            "url": "copied-poll",
            "due_date": "",
            "copy_choices": "on",
            "copy_ans_values": "on",
            "date_shift": "0",
        },
    )

    assert response.status_code == 302
    copied = Poll.objects.get(url="copied-poll")
    assert copied.title == "Copied poll"
    assert Choice.objects.filter(poll=copied, text=choice.text).exists()
    assert ChoiceValue.objects.filter(poll=copied, title=value.title).exists()


def test_poll_delete_post_deletes_poll(client, poll):
    client.force_login(poll.user)

    response = client.post(post_url("poll_delete", poll), {"Delete": "Delete"})

    assert response.status_code == 302
    assert not Poll.objects.filter(pk=poll.pk).exists()










