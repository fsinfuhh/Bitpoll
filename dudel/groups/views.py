from django.template.response import TemplateResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.http import Http404
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from .models import (GroupInvitation, GroupProxy, GroupError,
        create_usergroup)
from .forms import InvitationForm
from .signals import GroupOverview, show_group_overview


@login_required
def index(request):
    group = request.user.groups.order_by('name').first()
    if group:
        return redirect('groups_show', group.name)
    else:
        return TemplateResponse(request, 'groups/groups_base.html')


@login_required
def create(request):
    error = None
    group_name = ''
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        try:
            create_usergroup(request.user, group_name)
            msg = _('Group "{0}" was created.').format(group_name)
            messages.success(request, msg)
            return redirect('groups_show', group_name)
        except GroupError as e:
            error = e.message
    return TemplateResponse(request, 'groups/create.html', {
        'error': error,
        'group_name': group_name,
    })


@login_required
def show(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    properties = group.properties

    if not properties.public_members:
        can_see = (group.user_set.filter(pk=request.user.pk) or
                   GroupInvitation.objects.filter(group=group,
                                                  invitee=request.user))
        if not can_see:
            # We redirect to the group overview instead of HTTP 403
            # because a user might get redirected to this pager
            # after he had removed himself from the group
            return redirect('groups_index')

    group_members = list(group.user_set.order_by('first_name'))
    admin_pks = set(admin.pk for admin in properties.admins.all())
    is_groupadmin = request.user.pk in admin_pks
    num_admins = 0
    for group_member in group_members:
        group_member.is_groupadmin = group_member.pk in admin_pks
        if group_member.is_groupadmin:
            num_admins += 1

    if is_groupadmin:
        invitations = GroupInvitation.objects.filter(group=group)
    else:
        invitations = []

    panel_responses = show_group_overview.send(
        GroupOverview,
        group=group,
        members=group_members,
        is_admin=is_groupadmin,
        is_member=request.user in group_members)
    extra_panels = [response[1] for response in panel_responses
                    if response[1] is not None and
                       not isinstance(response[1], Exception)]

    return TemplateResponse(request, 'groups/show.html', {
        'group': group,
        'members': group_members,
        'invitations': invitations,
        'is_groupadmin': is_groupadmin,
        'last_admin': num_admins == 1,
        'extra_panels': extra_panels,
    })


@login_required
@require_POST
def leave(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    group_proxy = GroupProxy(group)
    try:
        group_proxy.remove_member(request.user, check_sole_admin=True)
        messages.success(request, _('You left the group.'))
    except GroupError as e:
        messages.error(request, e.message)
    
    return redirect('groups_index')


@login_required
@require_POST
def group_action(request, group_name, member_pk):
    group = get_object_or_404(Group, name=group_name)
    if not group.properties.admins.filter(pk=request.user.pk):
        raise PermissionDenied()
    
    User = get_user_model()
    try:
        member = group.user_set.get(pk=member_pk)
    except User.DoesNotExist:
        raise Http404
    group_proxy = GroupProxy(group)

    if 'kick' in request.POST:
        try:
            group_proxy.remove_member(member, check_sole_admin=True)
            messages.success(request, _('User was removed from group'))
        except GroupError as e:
            messages.errror(request, e.message)
    elif 'grant_admin' in request.POST:
        group_proxy.grant_admin(member)
        messages.success(request, _('User was granted group admin.'))
    elif 'revoke_admin' in request.POST:
        try:
            group_proxy.revoke_admin(member)
            messages.success(request, _('Revoked group admin rights from user.'))
        except GroupError as e:
            messages.errror(request, e.message)
    
    return redirect('groups_show', group.name) 


@login_required
def invite(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not group.properties.admins.filter(pk=request.user.pk):
        raise PermissionDenied()

    if request.method == 'POST':
        form = InvitationForm(request.POST, group=group,
                              user=request.user)
        if form.is_valid():
            subject = u'Neue Gruppeneinladung / new group invitation'
            invitations = form.get_invitations()
            for invitation in invitations:
                invitation.save()
                _send_invitation_mail(request, invitation, subject, 'new_invitation')
            messages.success(request, _('Invitation was sent.'))
            return redirect('groups_show', group_name)
    else:
        form = InvitationForm(group=group, user=request.user)

    return TemplateResponse(request, 'groups/invite.html', {
        'group': group,
        'form': form
    })


@login_required
@require_POST
def invitation_action(request, invitation_pk):
    invitation = get_object_or_404(GroupInvitation, pk=invitation_pk)
    if invitation.invitee != request.user:
        raise PermissionDenied()
    
    group = invitation.group
    if 'accept' in request.POST:
        invitation.accept()
        return redirect('groups_show', group.name)
    elif 'refuse' in request.POST:
        invitation.refuse()
    return redirect('groups_index')


@login_required
@require_POST
def withdraw_invite(request, invitation_pk):
    invitation = get_object_or_404(GroupInvitation, pk=invitation_pk)
    group = invitation.group
    if not group.properties.admins.filter(pk=request.user.pk):
        raise PermissionDenied()
    
    invitation.delete()
    return redirect('groups_show', group.name)


def _send_invitation_mail(request, invitation, subject, template_name):
    if not invitation.invitee.email:
        return
    old_lang = translation.get_language()
    translation.activate(invitation.invitee.language)
    template = loader.get_template('groups/mail_{0}.txt'.format(template_name))
    message = template.render({
        'invitation': invitation,
        'site': get_current_site(request)
    })
    translation.activate(old_lang)
    send_mail(settings.EMAIL_SUBJECT_PREFIX + subject,
              message,
              settings.DEFAULT_FROM_EMAIL,
              [invitation.invitee.email],
              fail_silently=True)

