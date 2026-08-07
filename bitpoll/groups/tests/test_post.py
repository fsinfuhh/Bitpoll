import pytest
from model_bakery import baker
from django.contrib.auth.models import Group
from django.urls import reverse

from bitpoll.groups.models import GroupInvitation


pytestmark = pytest.mark.django_db


@pytest.fixture
def group_data():
    admin = baker.make("base.BitpollUser", _fill_optional=True, username="group-admin")
    member = baker.make("base.BitpollUser", _fill_optional=True, username="group-member")
    group = baker.make(Group, _fill_optional=True, name="test-group")
    group.user_set.add(admin, member)
    group.properties.admins.add(admin)
    invitation = baker.make(
        GroupInvitation,
        _fill_optional=True,
        group=group,
        invitee=member,
        invited_by=admin,
    )
    return admin, member, group, invitation


def url(name, *args):
    return reverse(name, args=args)


def test_create_post_creates_group(client, admin_user=None):
    user = baker.make("base.BitpollUser", _fill_optional=True, username="creator")
    client.force_login(user)

    response = client.post(url("groups_create"), {"group_name": "new-group"})

    assert response.status_code == 302
    group = Group.objects.get(name="new-group")
    assert group.user_set.filter(pk=user.pk).exists()
    assert group.properties.admins.filter(pk=user.pk).exists()


def test_leave_post_removes_member(client, group_data):
    admin, member, group, _ = group_data
    client.force_login(member)

    response = client.post(url("groups_leave", group.name))

    assert response.status_code == 302
    assert not group.user_set.filter(pk=member.pk).exists()


def test_group_action_grants_admin(client, group_data):
    admin, member, group, _ = group_data
    client.force_login(admin)

    response = client.post(
        url("groups_action", group.name, member.pk),
        {"grant_admin": "Grant"},
    )

    assert response.status_code == 302
    assert group.properties.admins.filter(pk=member.pk).exists()


def test_group_action_kicks_member(client, group_data):
    admin, member, group, _ = group_data
    client.force_login(admin)

    response = client.post(
        url("groups_action", group.name, member.pk),
        {"kick": "Kick"},
    )

    assert response.status_code == 302
    assert not group.user_set.filter(pk=member.pk).exists()


def test_invitation_accept_post_adds_member(client, group_data):
    admin, member, group, invitation = group_data
    group.user_set.remove(member)
    client.force_login(member)

    response = client.post(
        url("groups_invitation_action", invitation.pk),
        {"accept": "Accept"},
    )

    assert response.status_code == 302
    assert group.user_set.filter(pk=member.pk).exists()
    assert not GroupInvitation.objects.filter(pk=invitation.pk).exists()


def test_invitation_refuse_post_deletes_invitation(client, group_data):
    admin, member, group, invitation = group_data
    client.force_login(member)

    response = client.post(
        url("groups_invitation_action", invitation.pk),
        {"refuse": "Refuse"},
    )

    assert response.status_code == 302
    assert not GroupInvitation.objects.filter(pk=invitation.pk).exists()


def test_withdraw_invite_post_deletes_invitation(client, group_data):
    admin, member, group, invitation = group_data
    client.force_login(admin)

    response = client.post(url("groups_withdraw_invite", invitation.pk))

    assert response.status_code == 302
    assert not GroupInvitation.objects.filter(pk=invitation.pk).exists()

