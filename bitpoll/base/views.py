import json
import string
import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.db.models import Q
from django.db import IntegrityError

from bitpoll.base.autocomplete import autocomplete_users
from bitpoll.base.models import BitpollUser
from bitpoll.caldav.forms import DavCalendarForm
from bitpoll.caldav.models import DavCalendar

from bitpoll.poll.forms import PollCreationForm
from bitpoll.poll.models import ChoiceValue, Poll, Vote, PollWatch

from bitpoll.base.models import USER_LANG
from bitpoll.base.forms import BitpollUserSettingsForm
from pytz import all_timezones

from bitpoll.registration.forms import RegisterForm
from bitpoll.settings import IMPRINT_URL
from django.core import signing
from django.conf import settings


def index(request):
    """
    :param request

    Takes title, type, due-date, url and public listening (boolean) of a poll as the user's input and checks the
    validity.
    If the input is valid, the poll and all possible choicevalues (yes, no and maybe) are saved. Depending on the
    poll-type, the user is directed to the type's choice-creation-site.

    If the input is not valid, the user is directed back for correction.
    """
    public_polls = Poll.objects.filter(public_listening=True)  # TODO: limit & sotierung & pagination oder so?
    randomize_url = settings.DEFAULT_RANDOM_SLUG == 'true'  # this settings value is a javascript true/false
    if request.method == 'POST':
        randomize_url = 'random_slug' in request.POST
        post_data = request.POST.copy()
        if randomize_url and request.POST.get('url', '') == '':
            post_data['url'] = generate_random_slug()
        form = PollCreationForm(post_data)
        if form.is_valid():
            current_poll = form.save()
            if request.user.is_authenticated:
                current_poll.user = request.user
                current_poll.save()
            # TODO: lazy translation
            # TODO: load from config
            ChoiceValue(title="yes", icon="check", color="90db46", weight=1, poll=current_poll).save()
            ChoiceValue(title="no", icon="ban", color="c43131", weight=0, poll=current_poll).save()
            ChoiceValue(title="maybe", icon="question", color="ffe800", weight=0.5, poll=current_poll).save()
            ChoiceValue(title="Only if absolutely necessary", icon="thumbs-down", color="B0E", weight=0.25,
                        poll=current_poll).save()

            if current_poll.type == 'universal':  # TODO: heir könnte auch auf die algemeine edit url weitergeleitet werden
                return redirect('poll_editUniversalChoice', current_poll.url)
            elif current_poll.type == 'date':
                return redirect('poll_editDateChoice', current_poll.url)
            else:
                return redirect('poll_editDTChoiceDate', current_poll.url)
    else:
        form = PollCreationForm()
    return TemplateResponse(request, "base/index.html", {
        'poll_form': form,
        'poll_count': Poll.objects.all().count(),
        'votes_count': Vote.objects.all().count(),
        'user_count': BitpollUser.objects.count(),
        'public_polls': public_polls,
        'randomize_url': randomize_url,
        'random_url': generate_random_slug() if randomize_url else '',
        'login_form': AuthenticationForm,
    })


def generate_random_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))


@login_required
def user_settings(request):
    polls = Poll.objects.filter(Q(user=request.user)
                                | Q(vote__user=request.user)
                                | Q(group__user=request.user)
                                | Q(pollwatch__user=request.user)
                                ).distinct().order_by('-due_date')

    if request.method == 'POST':
        user_form = BitpollUserSettingsForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()

            if request.user.auto_watch:
                for poll in polls.filter(Q(vote__user=request.user)):
                    try:
                        poll_watch = PollWatch(poll=poll, user=request.user)
                        poll_watch.save()
                    except IntegrityError:
                        pass
    else:
        user_form = BitpollUserSettingsForm(instance=request.user)

    return TemplateResponse(request, 'base/settings.html', {
        'polls': polls,
        'user': request.user,
        'user_form': user_form,
        'languages': USER_LANG,
        'timezones': all_timezones,
        'calendar_form': DavCalendarForm(user=request.user) if settings.CALENDAR_ENABLED else None,
        'calendars': DavCalendar.objects.filter(user=request.user) if settings.CALENDAR_ENABLED else None,
    })


def imprint(request):
    if IMPRINT_URL:
        return redirect(IMPRINT_URL)
    else:
        return TemplateResponse(request, 'base/imprint.html', {

        })


def about(request):
    return TemplateResponse(request, 'base/about.html', {

    })


def licenses(request):
    return TemplateResponse(request, 'base/licenses.html')


def tecnical(request):
    return TemplateResponse(request, 'base/technical_info.html')


def problems(request):
    team_email = settings.TEAM_EMAIL
    if not request.user.is_authenticated:
        team_email = team_email.replace(u'@', u' (AT) ')
    return TemplateResponse(request, 'base/problems.html', {
        'team_email': team_email
    })


@login_required
def autocomplete(request):
    term = request.GET.get('term', '')
    users = autocomplete_users(term)
    result_json = json.dumps({
    "users": [{
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        } for user in users]
    })
    return HttpResponse(result_json, content_type='application/json')