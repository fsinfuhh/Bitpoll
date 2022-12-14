from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from bitpoll.base.models import BitpollUser
from bitpoll.invitations.models import Invitation
from bitpoll.poll.models import Poll
from django.utils.translation import gettext_lazy as _


def invite(request, poll_url):
    current_poll = get_object_or_404(Poll, url=poll_url)
    error_msg = ""

    if request.method == 'POST':
        if not current_poll.can_edit(request.user, request):
            messages.error(
                request, _("You are not allowed to edit this Poll")
            )
        else:
            if 'resend_all' in request.POST:
                for invitation in current_poll.invitation_set:
                    invitation.send(request)
                return redirect('poll_settings', current_poll.url)

            elif 'resend' in request.POST:
                invitation_id = request.POST.get('resend', None)
                if invitation_id:
                    invitation = get_object_or_404(Invitation, pk=invitation_id)
                    invitation.send(request)
                return redirect('invitations', current_poll.url)

            elif 'delete' in request.POST:
                invitation_id = request.POST.get('delete', None)
                if invitation_id:
                    invitation = get_object_or_404(Invitation, id=invitation_id)
                    invitation.delete()
                return redirect('invitations', current_poll.url)

    return TemplateResponse(request, 'invitations/Invitation.html', {
        'poll': current_poll,
        'suppress_messages': True,
    })


@require_POST
def invitation_send(request, poll_url):
    current_poll = get_object_or_404(Poll, url=poll_url)
    user_error = ""
    if not current_poll.can_edit(request.user, request):
        messages.error(
            request, _("You are not allowed to edit this Poll")
        )
    else:
        receivers = request.POST.get('invite', None).split()
        for receiver in receivers:
            try:
                user = BitpollUser.objects.get(username=receiver)
                invitation = Invitation(user=user, poll=current_poll, date_created=now(), creator=request.user,
                                        vote=None)
                invitation.save()
                invitation.send(request)
            except IntegrityError:
                messages.warning(request, _("The user {} was already invited".format(receiver)))
            except ObjectDoesNotExist:
                try:
                    group = Group.objects.get(name=receiver)
                    for group_user in group.user_set.all():
                        try:
                            invitation = Invitation(user=group_user, poll=current_poll, date_created=now(),
                                                    creator=request.user, vote=None)
                            invitation.save()
                            invitation.send(request)
                        except IntegrityError:
                            # One user is already invited, ignore it
                            pass
                except ObjectDoesNotExist:
                    user_error += " '{}'".format(receiver)
        if user_error:
            messages.error(
                request, _("The following User/Groups could not be found:  {}".format(user_error))
            )
    return redirect('invitations', current_poll.url)
