from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.db.models import Q

from dudel.base.models import DudelUser
from dudel.base.forms import DudelUserForm

from dudel.poll.forms import PollCreationForm
from dudel.poll.models import ChoiceValue, Poll, Vote

from dudel.base.models import USER_LANG
from pytz import all_timezones
from dudel.settings import IMPRINT_URL


def login(request):
    pass


def index(request):
    """
    :param request

    Takes title, type, due-date, url and public listening (boolean) of a poll as the user's input and checks the
    validity.
    If the input is valid, the poll and all possible choicevalues (yes, no and maybe) are saved. Depending on the
    poll-type, the user is directed to the type's choice-creation-site.

    If the input is not valid, the user is directed back for correction.
    """
    public_polls = Poll.objects.filter(public_listening=True)
    if request.method == 'POST':
        form = PollCreationForm(request.POST)
        if form.is_valid():
            current_poll = form.save()
            if request.user.is_authenticated():
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
        'user_count': DudelUser.objects.count(),
        'public_polls': public_polls,
    })


def settings(request):
    if request.user.is_authenticated():
        polls = Poll.objects.filter(Q(user=request.user) | Q(vote__user=request.user) |
                                    Q(group__user=request.user)).distinct().order_by('created')

        if request.method == 'POST':
            form = DudelUserForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()

        user_form = DudelUserForm(instance=request.user)

        return TemplateResponse(request, 'base/settings.html', {
            'polls': polls,
            'user': request.user,
            'user_form': user_form,
            'languages': USER_LANG,
            'timezones': all_timezones,
        })


def imprint(request):
    if IMPRINT_URL:
        return redirect(IMPRINT_URL)
    else:
        return TemplateResponse(request, 'base/imprint.html', {

        })
