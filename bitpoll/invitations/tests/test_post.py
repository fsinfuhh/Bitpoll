import pytest
from model_bakery import baker
from django.urls import reverse

from bitpoll.invitations.models import Invitation
from bitpoll.poll.models import Poll


pytestmark = pytest.mark.django_db


@pytest.fixture
def invitation_data():
    owner = baker.make("base.BitpollUser", _fill_optional=True, username="invitation-owner")
    invitee = baker.make("base.BitpollUser", _fill_optional=True, username="invitation-user")
    poll = baker.make(
        Poll,
        _fill_optional=True,
        title="Invitation poll",
        url="invitation-poll",
        type="universal",
        user=owner,
        require_login=False,
        require_invitation=False,
        due_date=None,
    )
    invitation = baker.make(
        Invitation,
        _fill_optional=True,
        creator=owner,
        user=invitee,
        poll=poll,
        vote=None,
    )
    return owner, invitee, poll, invitation


def test_invitation_delete_post_deletes_invitation(client, invitation_data):
    owner, invitee, poll, invitation = invitation_data
    client.force_login(owner)

    response = client.post(
        reverse("invitations", args=[poll.url]),
        {"delete": str(invitation.pk)},
    )

    assert response.status_code == 302
    assert not Invitation.objects.filter(pk=invitation.pk).exists()


def test_invitation_send_post_creates_invitation(client, invitation_data):
    owner, invitee, poll, invitation = invitation_data
    invitation.delete()
    client.force_login(owner)

    response = client.post(
        reverse("invitations_send", args=[poll.url]),
        {"invite": invitee.username},
    )

    assert response.status_code == 302
    created = Invitation.objects.get(poll=poll, user=invitee)
    assert created.creator == owner

