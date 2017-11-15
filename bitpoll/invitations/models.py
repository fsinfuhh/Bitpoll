from smtplib import SMTPRecipientsRefused

from django.contrib import messages
from django.core.mail import send_mail
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from bitpoll.base.models import BitpollUser
from bitpoll.poll.models import Poll, Vote

from datetime import timedelta


class Invitation(models.Model):
    class Meta:
        unique_together = ('user', 'poll')

    date_created = models.DateTimeField()
    creator = models.ForeignKey(BitpollUser, on_delete=models.CASCADE, related_name='creator')
    user = models.ForeignKey(BitpollUser, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    vote = models.ForeignKey(Vote, on_delete=models.SET_NULL, null=True, blank=True)
    last_email = models.DateTimeField(null=True, blank=True)

    def send(self, request):
        if (not self.last_email) or self.last_email + timedelta(hours=12) < now():  # TODO: TIMEDELTA mit config
            old_lang = translation.get_language()
            translation.activate(self.user.language)
            link = reverse('poll_vote', args=(self.poll.url,))  # TODO: hier direkt das poll oder das Vote?
            email_content = render_to_string('invitations/mail_invite.txt', {
                'receiver': self.user.username,
                'creator': self.creator.username,
                'link': link
            })
            try:
                send_mail("Invitation to vote on {}".format(self.poll.title), email_content, None, [self.user.email])
                self.last_email = now()
                self.save()
            except SMTPRecipientsRefused:
                translation.activate(old_lang)
                messages.error(
                    request, _("The mail server had an error sending the notification to {}".format(self.user.username))
                )
            translation.activate(old_lang)
        else:
            messages.error(
                request, _("You have send an Email for {} in the last 12 Hours".format(self.user.username))
            )

    def can_edit(self, user: BitpollUser, request: HttpRequest=None):
        return self.poll.can_edit(user, request)

    def __str__(self):
        return u'Invitation {}'.format(self.id)
