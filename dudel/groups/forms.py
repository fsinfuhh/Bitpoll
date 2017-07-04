from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from mafiasi.groups.models import GroupInvitation

class InvitationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        self.user = kwargs.pop('user')
        super(InvitationForm, self).__init__(*args, **kwargs)

    invitees = forms.CharField()
    invitee_users = []

    def clean_invitees(self):
        self.invitee_users = []
        data = self.cleaned_data['invitees']
        invitees = [s.strip() for s in data.split(',')]
        for invitee in invitees:
            User = get_user_model()
            try:
                invitee_user = User.objects.get(username=invitee)
                self.invitee_users.append(invitee_user)
            except User.DoesNotExist:
                raise forms.ValidationError(_('There is no user "%s."')
                                            % invitee)

            has_invitation = bool(GroupInvitation.objects.filter(
                    group=self.group, invitee=invitee_user))
            if has_invitation:
                raise forms.ValidationError(
                    _('"%s" already has an invitation.') % invitee)

            already_member = \
                invitee_user.groups.filter(name=self.group.name).exists()
            if already_member:
                raise forms.ValidationError(
                    _('"%s" is already a member of this group.')
                    % invitee)

    def get_invitations(self):
        invitations = []
        for invitee_user in self.invitee_users:
            invitations.append(GroupInvitation(group=self.group,
                                invitee=invitee_user,
                                invited_by=self.user))
        return invitations

    def save(self):
        self.get_invitation().save()
