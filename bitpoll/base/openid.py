from urllib.parse import quote

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from simple_openid_connect.data import TokenSuccessResponse
from simple_openid_connect.integrations.django.apps import OpenidAppConfig
from simple_openid_connect.integrations.django.models import OpenidUser
from simple_openid_connect.integrations.django.user_mapping import UserMapper


class BitpollUserMapper(UserMapper):
    def handle_federated_userinfo(self, user_data):
        # if there is already a user with this username, we create the openid association if it does not exist yet
        User = get_user_model()
        try:
            user = User.objects.get(username=user_data.preferred_username)
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
        if hasattr(user_data, "display_name"):
            user.displayname = user_data.display_name
            user.save()
        
        groups = getattr(user_data, "groups", [])
        for group_name in groups:
            group = Group.objects.get_or_create(name=group_name)[0]
            group.user_set.add(user)
            group.save()
            if settings.OPENID_ADMIN_GROUPS.fullmatch(group.name) is not None:
                user.is_superuser = True
                user.is_staff = True


def refresh_group_users(group: Group):
    # get users from openid
    # request token

    CACHE_KEY_ACCESS_TOKEN = "bitpoll.oidc_access_token"
    CACHE_KEY_REFRESH_TOKEN = "bitpoll.oidc_refresh_token"

    def oidc_expiry2cache_expiry(n: int) -> int | None:
        """
        Openid encodes *never-expires* as `0` while django treats `0` as don't cache.
        This function rewrites `0` to `None` which is the django representation for *never-expires*.
        """
        if n == 0:
            return None
        else:
            return n

    oidc_client = OpenidAppConfig.get_instance().get_client()
    access_token = cache.get(CACHE_KEY_ACCESS_TOKEN)
    if access_token is None:
        refresh_token = cache.get(CACHE_KEY_REFRESH_TOKEN)
        if refresh_token is None:
            # get completely new tokens
            token_response = oidc_client.client_credentials_grant.authenticate()
        else:
            # use the cached refresh token to get a new access token
            token_response = oidc_client.exchange_refresh_token(refresh_token)

        # save the new tokens
        assert isinstance(token_response, TokenSuccessResponse), f"Could not get new tokens: {token_response}"
        access_token = token_response.access_token
        cache.set(
            key=CACHE_KEY_ACCESS_TOKEN,
            value=token_response.access_token,
            timeout=oidc_expiry2cache_expiry(token_response.expires_in),
        )
        if token_response.refresh_token:
            cache.set(
                key=CACHE_KEY_REFRESH_TOKEN,
                value=token_response.refresh_token,
                timeout=oidc_expiry2cache_expiry(token_response.refresh_expires_in),
            )

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
