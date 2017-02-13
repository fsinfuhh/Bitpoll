from django.shortcuts import redirect
from django.template.response import TemplateResponse

from dudel.poll.forms import PollCreationForm
from dudel.poll.models import ChoiceValue


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
    if request.method == 'POST':
        form = PollCreationForm(request.POST)
        if form.is_valid():
            current_poll = form.save()
            # TODO: lazy translation
            # TODO: load from config
            ChoiceValue(title="yes", icon="check", color="90db46", weight=1, poll=current_poll).save()
            ChoiceValue(title="no", icon="ban", color="c43131", weight=0, poll=current_poll).save()
            ChoiceValue(title="maybe", icon="question", color="ffe800", weight=0.5, poll=current_poll).save()
            ChoiceValue(title="Only if absolutely necessary", icon="thumbs-down", color="B0E", weight=0.25,
                        poll=current_poll).save()

            if current_poll.type == 'universal':
                return redirect('poll_editUniversalChoice', current_poll.url)
            elif current_poll.type == 'date':
                return redirect('poll_editDateChoice', current_poll.url)
            else:
                return redirect('poll_editDTChoiceDate', current_poll.url)
    else:
        form = PollCreationForm()
    return TemplateResponse(request, "base/index.html", {
        'new_Poll': form
    })