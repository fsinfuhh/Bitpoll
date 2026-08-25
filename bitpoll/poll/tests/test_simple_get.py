import pytest
from django.utils.timezone import now

from bitpoll.poll.models import Choice, ChoiceValue, Comment, Poll, Vote, VoteChoice
from bitpoll.tests._base import get_dynamic_url, get_module_urls


URLS = get_module_urls("poll")


@pytest.fixture
def poll(db, django_user_model):
    user = django_user_model.objects.create_user(username="poll-owner", password="password")
    return Poll.objects.create(title="Test poll", url="test-poll", type="universal", user=user)


@pytest.fixture
def comment(poll):
    return Comment.objects.create(
        text="Test comment",
        date_created=now(),
        name="Poll owner",
        user=poll.user,
        poll=poll,
    )


@pytest.fixture
def vote(poll):
    choice = Choice.objects.create(text="Test choice", poll=poll, sort_key=0)
    choice_value = ChoiceValue.objects.create(
        title="Yes", icon="check", color="00ff00", poll=poll
    )
    vote = Vote.objects.create(
        name="Test voter",
        date_created=now(),
        comment="",
        poll=poll,
    )
    VoteChoice.objects.create(comment="", value=choice_value, vote=vote, choice=choice)
    return vote


def url_args(url_name, poll, comment, vote):
    if url_name in {"poll_comment_edit", "poll_deleteComment"}:
        return [poll.url, comment.pk]
    if url_name in {"poll_voteAssign", "poll_voteEdit", "poll_voteDelete"}:
        return [poll.url, vote.pk]
    return [poll.url]


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_without_login(client, poll, comment, vote, url_name, arg_count):
    response = client.get(get_dynamic_url(url_args(url_name, poll, comment, vote), url_name))
    match url_name:
        case "poll_comment_edit":
            assert response.status_code == 302
        case "poll_watch" | "poll_editchoicevalues_create":
            assert response.status_code == 405
        case "poll_settings" | "poll_editChoice" | "poll_editDateChoice" | "poll_editDTChoiceDate" | "poll_editDTChoiceTime" | "poll_editDTChoiceCombinations" | "poll_editUniversalChoice" | "poll_editchoicevalues" | "poll_copy":
            assert response.status_code == 302
        case _:
            assert response.status_code == 200


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_with_login(client, poll, comment, vote, url_name, arg_count):
    client.force_login(poll.user)
    response = client.get(get_dynamic_url(url_args(url_name, poll, comment, vote), url_name))
    match url_name:
        case "poll_watch" | "poll_editchoicevalues_create":
            assert response.status_code == 405
        case "poll_editChoice" | "poll_editDTChoiceTime" | "poll_editDTChoiceCombinations":
            assert response.status_code == 302
        case _:
            assert response.status_code == 200


