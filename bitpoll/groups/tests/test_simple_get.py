import pytest
from django.contrib.auth.models import Group

from bitpoll.groups.models import GroupInvitation
from bitpoll.tests._base import get_dynamic_url, get_module_urls


URLS = get_module_urls("groups")


@pytest.fixture
def group_data(db, django_user_model):
    user = django_user_model.objects.create_user(username="group-user", password="password")
    group = Group.objects.create(name="test-group")
    group.user_set.add(user)
    group.properties.admins.add(user)
    invitation = GroupInvitation.objects.create(group=group, invitee=user, invited_by=user)
    return user, group, invitation


def url_args(url_name, group, invitation):
    if "groups_action" in url_name:
        return [group.name, group.user_set.first().pk]
    if "invitation" in url_name or "withdraw" in url_name:
        return [invitation.pk]
    if "groups_" in url_name and url_name != "groups_index" and url_name != "groups_create":
        return [group.name]
    return []


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_without_login(client, group_data, url_name, arg_count):
    _, group, invitation = group_data
    response = client.get(get_dynamic_url(url_args(url_name, group, invitation), url_name))
    match url_name:
        case "groups_index" | "groups_create" | "groups_show" | "groups_leave" | "groups_invite" | "groups_action" | "groups_invitation_action" | "groups_withdraw_invite":
            assert response.status_code == 302
        case _:
            assert response.status_code == 200


@pytest.mark.parametrize("url_name,arg_count", URLS)
def test_urls_with_login(client, group_data, url_name, arg_count):
    user, group, invitation = group_data
    client.force_login(user)
    response = client.get(get_dynamic_url(url_args(url_name, group, invitation), url_name))
    match url_name:
        case "groups_index":
            assert response.status_code == 302
        case "groups_leave" | "groups_action" | "groups_invitation_action" | "groups_withdraw_invite":
            assert response.status_code == 405
        case _:
            assert response.status_code == 200



