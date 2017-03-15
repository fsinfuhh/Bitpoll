from datetime import datetime

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse

from dudel.base.models import DudelUser
from dudel.invitations.models import Invitation
from dudel.poll.models import Poll


def invite(request, poll_url):
    current_poll = get_object_or_404(Poll, url=poll_url)
    error_msg = ""

    if request.method == 'POST':
        if not current_poll.can_edit(request.user):
            error_msg = "Not allowed to edit"
        else:
            if 'resend_all' in request.POST:
                for invitation in current_poll.invitation_set:
                    invitation.send()
                return redirect('poll_settings', current_poll.url)

            elif 'resend' in request.POST:
                invitation_id = request.POST.get('resend', None)
                if invitation_id:
                    invitation = get_object_or_404(Invitation, pk=invitation_id)
                    invitation.send()
                return redirect('invitations', current_poll.url)

            elif 'delete' in request.POST:
                invitation_id = request.POST.get('delete', None)
                if invitation_id:
                    invitation = get_object_or_404(Invitation, id=invitation_id)
                    invitation.delete()
                return redirect('invitations', current_poll.url)

    return TemplateResponse(request, 'invitations/Invitation.html', {
        'poll': current_poll,
    })


def invitation_send(request, poll_url):
    current_poll = get_object_or_404(Poll, url=poll_url)
    error_msg = ""

    if request.method == 'POST':
        if not current_poll.can_edit(request.user):
            error_msg = "Not allowed to edit"
        else:
            receivers = request.POST.get('invite', None).split()
            for receiver in receivers:
                try:
                    user = DudelUser.objects.get(username=receiver)
                    invitation = Invitation(user=user, poll=current_poll, date_created=datetime.now(), creator=request.user,
                                            last_invited=datetime.now(), vote=None)
                    invitation.save()
                    invitation.send()
                except ObjectDoesNotExist:
                    try:
                        group = Group.objects.get(name=receiver)
                        for group_user in group.user_set:
                            invitation = Invitation(user=group_user, poll=current_poll, date_created=datetime.now(),
                                                    creator=request.user, last_invited=datetime.now(), vote=None)
                            invitation.save()
                            invitation.send()
                    except ObjectDoesNotExist:
                        user_error = "Receiver not Found"  # TODO error msg

        return redirect('invitations', current_poll.url)
