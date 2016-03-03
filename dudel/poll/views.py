from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
# from django.http import HttpResponseRedirect
from .forms import PollCreationForm, DateChoiceCreationForm, UniversalChoiceCreationForm, DTChoiceCreationDateForm, DTChoiceCreationTimeForm
from .models import Poll, Choice, ChoiceValue

# Create your views here.


"""
    Displays for a given poll its fields along with all possible choices.
"""
def poll(request, poll_url):
    poll = get_object_or_404(Poll, url=poll_url)
    return TemplateResponse(request, "poll/poll.html", {
        'poll': poll,
    })


"""
    Takes title, type, due-date, url and public listening (boolean) of a poll as the user's input and checks the
    validity.
    If the input is valid, the poll and all possible choicevalues (yes, no and maybe) are saved. Depending on the
    poll-type, the user is directed to the type's choice-creation-site.

    If the input is not valid, the user is directed back for correction.
"""
def index(request):
    if request.method == 'POST':
        form = PollCreationForm(request.POST)
        if form.is_valid():
            poll = form.save()
            ChoiceValue(title="yes", icon="", color="#9C6", weight=1, poll=poll).save()
            ChoiceValue(title="no", icon="", color="#F96", weight=0, poll=poll).save()
            ChoiceValue(title="maybe", icon="", color="#FF6", weight=0.5, poll=poll).save()

            if poll.type == 'universal':
                return redirect('poll_editUniversalChoice', poll.url)
            elif poll.type == 'date':
                return redirect('poll_editDateChoice', poll.url)
            else:
                return redirect('poll_editDTChoiceDate', poll.url)
    else:
        form = PollCreationForm()
    return TemplateResponse(request, "poll/index.html", {
        'new_Poll': form
    })


def delete_comment(request, comment_id):
    pass


def edit(request, poll_id):
    pass


def watch(request, poll_id):
    pass


def edit_choice(request, poll_id):
    pass


"""
    Takes several dates as the user's input und checks the validity.
    If the input is valid, for every given date a choice is created and saved. The user is directed to the poll's site.

    If the input is not valid, the user is directed back for correction.
"""
def edit_date_choice(request, poll_url):
    poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        form = DateChoiceCreationForm(request.POST)
        if form.is_valid():
            for datum in form.cleaned_data['date'].split(";"):
                choice = Choice(text="", date=datum, poll=poll)
                choice.save()
            return redirect('poll', poll_url)
    else:
        form = DateChoiceCreationForm()
    return TemplateResponse(request, "poll/DateChoiceCreation.html", {
        'new_Choice': form
    })


def edit_date_time_choice(request, poll_url):
    pass


"""
    Takes several dates as the user's input and checks if it's valid.
    If the data is valid, the user is directed to the time-input-site. (The date is passed on as an argument)

    If the data is not valid, the user is directed back for correction.
"""
def edit_dt_choice_date(request, poll_url):
    poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        form = DTChoiceCreationDateForm(request.POST)
        if form.is_valid():
            time = DTChoiceCreationTimeForm({'date': form.cleaned_data['date']})
            return TemplateResponse(request, "poll/DTChoiceCreationTime.html", {
                'time': time,
                'poll_url': poll.url,
            })
    else:
        form = DTChoiceCreationDateForm()
    return TemplateResponse(request, "poll/DTChoiceCreationDate.html", {
        'new_Choice': form
    })


"""
    Takes several times as the user's input and checks the validity.
    If the data is valid, the user is directed to the combinations-site, to which all possible combinations of
        dates and times are passed on.
    If the dates are missing, the user is directed back to the date-input-site.
    If the times are missing, the user is directed back to the time-input-site.
"""
def edit_dt_choice_time(request, poll_url):
    poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        form = DTChoiceCreationTimeForm(request.POST)
        if form.is_valid():
            times = form.cleaned_data['time'].split(',')
            dates = form.cleaned_data['data'].split(';')
            for time in times:
                for date in dates:
                    pass
        elif form.cleaned_data['date'] != "":
            return TemplateResponse(request, "poll/DTChoiceCreationTime.html", {
                'time': form,
                'poll_url': poll.url,
            })
        else:
            return redirect('poll_editDTChoiceDate', poll.url)

    else:
        return redirect('poll_editDTChoiceDate', poll.url)


def edit_dt_choice_combinations(request, poll_url):
    pass


"""
    Takes the text of a choice as the user's input and checks its validity.
    If the input is valid, the choice is saved (with 01.01.1970 as date) and the user is directed to the poll's site.

    If the input is not valid, the user is directed back for correction.
"""
def edit_universal_choice(request, poll_url):
    poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        form = UniversalChoiceCreationForm(request.POST)
        if form.is_valid():
            choice = Choice(text=form.cleaned_data['text'], date='1970-01-01', poll=poll)
            choice.save()
            return redirect('poll', poll_url)
    else:
        form = UniversalChoiceCreationForm()
    return TemplateResponse(request, "poll/UniversalChoiceCreation.html", {
        'new_Choice': form
    })


def values(request, poll_id):
    pass


def delete(request, poll_id):
    pass


def vote(request, poll_id):
    pass


def vote_assign(request, poll_id, vote_id):
    pass


def vote_edit(request, poll_id, vote_id):
    pass


def vote_delete(request, poll_id, vote_id):
    pass


def copy(request, poll_id):
    pass
