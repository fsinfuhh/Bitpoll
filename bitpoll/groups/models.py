import re

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


MIN_GROUPNAME_LENGTH = 3


class GroupError(Exception):
    def __init__(self, message):
        self.message = message


class GroupProperties(models.Model):
    group = models.OneToOneField(Group, related_name='properties', on_delete=models.CASCADE)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL,
            related_name='admin_of')
    public_members = models.BooleanField(default=False)


class GroupProxy(object):
    def __init__(self, group):
        self.group = group

    def add_member(self, user):
        group = self.group
        group.user_set.add(user)

    def remove_member(self, user, check_sole_admin=False):
            properties = self.group.properties
            if check_sole_admin:
                self._raise_if_sole_admin(user)
            properties.admins.remove(user)
            self.group.user_set.remove(user)
    
    def grant_admin(self, user):
        self.group.properties.admins.add(user)

    def revoke_admin(self, user):
        self._raise_if_sole_admin(user)
        self.group.properties.admins.remove(user)

    def is_admin(self, user):
        return bool(self.group.properties.admins.filter(pk=user.pk).count())

    def is_member(self, user):
        return bool(self.group.user_set.filter(pk=user.pk).count())

    def _raise_if_sole_admin(self, user):
        properties = self.group.properties
        if self.is_admin(user):
            num_admins = properties.admins.count()
            if num_admins == 1:
                msg = _('You are the sole group admin. Please terminate the '
                        'group or appoint another group admin.')
                raise GroupError(msg)


class GroupInvitation(models.Model):
    date_invited = models.DateTimeField(default=now)
    group = models.ForeignKey(Group, related_name='invitations', on_delete=models.CASCADE)
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL,
            related_name='invitations', on_delete=models.CASCADE)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
            related_name='given_invitations', on_delete=models.CASCADE)

    def __unicode__(self):
        return u'Invitation to {0} for {1}'.format(self.group, self.invitee)

    def accept(self):
        group_proxy = GroupProxy(self.group)
        group_proxy.add_member(self.invitee)
        self.delete()

    def refuse(self):
        self.delete()


# also used in the URL so if you no longer allow something
# existing groups are no longer accessible
group_name_regex = r'[a-zA-Z][a-zA-Z0-9\-\.]*'
_group_name_re = re.compile("^{}$".format(group_name_regex))


def create_usergroup(user, name):
    if not _group_name_re.match(name):
        raise GroupError(_('Invalid group name.'))

    if len(name) < MIN_GROUPNAME_LENGTH:
        err_msg = _('The group name must be at least {} characters').format(
                MIN_GROUPNAME_LENGTH)
        raise GroupError(err_msg)
    
    if Group.objects.filter(name__iexact=name).count():
        raise GroupError(_('Group does already exist.'))
    
    group = Group.objects.create(name=name)

    group_proxy = GroupProxy(group)
    group_proxy.add_member(user)

    group.properties.admins.add(user)

    return group


def _change_group_cb(sender, instance, created, **kwargs):
    if created:
        props = GroupProperties.objects.create(group=instance)
        instance.properties = props

post_save.connect(_change_group_cb, sender=Group)
