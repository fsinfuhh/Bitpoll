from urllib.parse import quote

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from simple_openid_connect.integrations.django.models import OpenidUser
from simple_openid_connect.integrations.django.user_mapping import UserMapper


class BitpollUserMapper(UserMapper):
    def handle_federated_userinfo(self, user_data):
        # if there is already a user with this username, we create the openid association if it does not exist yet
        User = get_user_model()
        try:
            user = User.objects.get(username=user_data.username)
            OpenidUser.objects.get_or_create(
                sub=user_data.sub,
                defaults={
                    "user": user,
                },
            )
        except User.DoesNotExist:
            # if the user does not exist, it is automatically created by the super class
            pass
        return super().handle_federated_userinfo(user_data)

    def automap_user_attrs(self, user, user_data):
        super().automap_user_attrs(user, user_data)
        for group_name in user_data.groups:
            group = Group.objects.get_or_create(name=group_name)[0]
            group.user_set.add(user)
            group.save()


def refresh_group_users(group: Group):
    # get users from openid
    # request token
    response = requests.post(
        settings.OPENID_ISSUER + "/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": settings.OPENID_CLIENT_ID,
            "client_secret": settings.OPENID_CLIENT_SECRET,
            "scope": "openid profile email roles",
        },
    )
    access_token = response.json()["access_token"]
    # get group id
    response = requests.get(
        settings.OPENID_API_BASE + "/groups?exact=true&search=" + quote(group.name),
        headers={"Authorization": "Bearer " + access_token},
    )
    group_id = response.json()[0]["id"]
    # get users
    response = requests.get(
        settings.OPENID_API_BASE
        + "/groups/"
        + group_id
        + "/members?briefRepresentation=true",
        headers={"Authorization": "Bearer " + access_token},
    )
    # add users to group
    User = get_user_model()
    for user_json in response.json():
        user = User.objects.get_or_create(
            username=user_json["username"],
            defaults={
                "first_name": user_json["firstName"],
                "last_name": user_json["lastName"],
                "email": user_json["email"],
            },
        )[0]
        group.user_set.add(user)
    group.save()
