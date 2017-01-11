import re
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from .forms import PollCreationForm, PollCopyForm, DateChoiceCreationForm, UniversalChoiceCreationForm, \
    DTChoiceCreationDateForm, DTChoiceCreationTimeForm
from .models import Poll, Choice, ChoiceValue, Vote, VoteChoice, Comment
from datetime import datetime


def poll(request, poll_url):
    """
    :param request
    :param poll_url: url of poll

    Displays for a given poll its fields along with all possible choices, all votes and all its comments.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        new_comment = Comment(text=request.POST['newCom'],
                              date_created=datetime.now(),
                              name=request.POST['newComName'],
                              poll=current_poll,
                              user=request.user)
        new_comment.save()
        # return redirect('poll', poll_url)

    poll_votes = Vote.objects.filter(poll=current_poll).order_by(
        'name').select_related()
    # prefetch_related('votechoice_set').select_releated() #TODO (Prefetch objekt nötig, wie ist der reverse join name wirklich?

    return TemplateResponse(request, "poll/poll.html", {
        'poll': current_poll,
        'page': '',
        'votes': poll_votes,
    })


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
            ChoiceValue(title="maybe", icon="check", color="ffe800", weight=0.5, poll=current_poll).save()
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
    return TemplateResponse(request, "poll/index.html", {
        'new_Poll': form
    })


def comment(request, poll_url):
    pass


def edit_comment(request, poll_url, comment_id):
    pass


def delete_comment(request, poll_url, comment_id):
    """
    :param request:
    :param poll_url: url of poll belonging to comment
    :param comment_id: ID of comment to be deleted
    :return:

    Case Delete:
        If the user is authenticated and equal to the saved user of the comment, the comment is deleted
        and the user is directed back to the poll's page

        If the user is authenticated but differs from the saved user of the comment, the user is directed
        back with error message "Deletion not allowed. You are not [comment.name]"

        Without authentication the user is directed back with error message "Deletion not allowed.
        You are not authenticated."

    Case Cancel:
        The user is redirected back to the poll's page.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    current_comment = get_object_or_404(Comment, id=comment_id)
    error_msg = ""

    if request.method == 'POST':
        if 'Delete' in request.POST:
            if request.user.is_authenticated():
                # TODO additional possibilities of deleting
                if request.user == current_comment.user:
                    current_comment.delete()
                    return redirect('poll', poll_url)
                else:
                    error_msg = "Deletion not allowed. You are not " + str(current_comment.name) + "."
            else:
                error_msg = "Deletion not allowed. You are not authenticated."
        else:
            return redirect('poll', poll_url)

    return TemplateResponse(request, 'poll/CommentDelete.html', {
        'poll': current_poll,
        'comment': current_comment,
        'error': error_msg,
    })


def edit(request, poll_url):
    pass


def watch(request, poll_url):
    pass


def edit_choice(request, poll_url):
    # TODO: doppelung mit oben im index, muss das?
    current_poll = get_object_or_404(Poll, url=poll_url)
    if current_poll.type == 'universal':
        return redirect('poll_editUniversalChoice', current_poll.url)
    elif current_poll.type == 'date':
        return redirect('poll_editDateChoice', current_poll.url)
    else:
        return redirect('poll_editDTChoiceDate', current_poll.url)
    pass


def edit_date_choice(request, poll_url):
    """
    :param request:
    :param poll_url: url of poll

    Takes several dates as the user's input und checks the validity.
    If the input is valid, for every given date a choice is created and saved. The user is directed to the poll's site.

    If the input is not valid, the user is directed back for correction.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        form = DateChoiceCreationForm(request.POST)
        if form.is_valid():
            for i, datum in enumerate(sorted(form.cleaned_data['dates'].split(";"))):
                choice = Choice(text="", date=datum, poll=current_poll, sort_key=i)
                choice.save()
            return redirect('poll', poll_url)
    else:
        form = DateChoiceCreationForm()
    return TemplateResponse(request, "poll/DateChoiceCreation.html", {
        'poll': current_poll,
        'new_Choice': form,
        'page': 'Choices',
    })


def edit_date_time_choice(request, poll_url):
    pass


def edit_dt_choice_date(request, poll_url):
    """
    :param request:
    :param poll_url: url of poll

    Takes several dates as the user's input and checks if it's valid.
    If the data is valid, the user is directed to the time-input-site. (The date is passed on as an argument)

    If the data is not valid, the user is directed back for correction.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        form = DTChoiceCreationDateForm(request.POST)
        if form.is_valid():
            time = DTChoiceCreationTimeForm({'dates': form.cleaned_data['dates']})
            return TemplateResponse(request, "poll/DTChoiceCreationTime.html", {
                'time': time,
                'poll': current_poll,
                'step': 2,
            })
    else:
        form = DTChoiceCreationDateForm()
    return TemplateResponse(request, "poll/DTChoiceCreationDate.html", {
        'new_Choice': form,
        'poll': current_poll,
        'step': 1,
        'page': 'Choices',
    })


def edit_dt_choice_time(request, poll_url):
    """
    :param request:
    :param poll_url: url of poll

    Takes several times as the user's input and checks the validity.
    If the data is valid, the user is directed to the combinations-site, to which all possible combinations of
        dates and times are passed on.
    If the dates are missing, the user is directed back to the date-input-site.
    If the times are missing, the user is directed back to the time-input-site.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        form = DTChoiceCreationTimeForm(request.POST)
        if form.is_valid():
            times = form.cleaned_data['times'].split(',')
            dates = form.cleaned_data['dates'].split(',')

            return TemplateResponse(request, "poll/DTChoiceCreationCombinations.html", {
                'times': times,
                'dates': dates,
                'poll': current_poll,
            })
        elif form.cleaned_data['date'] != "":
            return TemplateResponse(request, "poll/DTChoiceCreationTime.html", {
                'time': form,
                'poll': current_poll,
            })
    return redirect('poll_editDTChoiceDate', current_poll.url)


def edit_dt_choice_combinations(request, poll_url):
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        # getlist does not raise an exception if datetimes[] is not in request.POST
        chosen_combinations = request.POST.getlist('datetimes[]')

        # parse datetime objects of chosen combinations
        choices = []
        for combination in chosen_combinations:
            try:
                choices.append(datetime.strptime(combination, '%Y-%m-%d %H:%M'))
            except ValueError:
                # at least one invalid time/date has been specified. Redirect to first step
                return redirect('poll_editDTChoiceDate', current_poll.url)

        # all combinations have been valid. save choices to database.
        for i, choice in enumerate(sorted(choices)):
            Choice.objects.create(
                date=choice, poll=current_poll, sort_key=i)
        return redirect('poll', current_poll.url)
    return redirect('poll_editDTChoiceDate', current_poll.url)


def edit_universal_choice(request, poll_url):
    """
    :param request:
    :param poll_url: url of poll

    Takes the text of a choice as the user's input and checks its validity.
    If the input is valid, the choice is saved and the user is directed to the poll's site.

    If the input is not valid, the user is directed back for correction.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        # save new choices
        choice_texts = request.POST.getlist('choice_text')
        for choice_text in choice_texts:
            choice_text = choice_text.strip()
            if choice_text == '':
                continue
            choice = Choice(text=choice_text, poll=current_poll)
            choice.save()

        # update existing choices
        pattern = re.compile(r'^choice_text_(\d+)$')
        for choice_id in request.POST.keys():
            choice = pattern.match(choice_id)
            if not choice:
                continue
            pk = choice.group(1)
            db_choice = get_object_or_404(Choice, poll=current_poll, pk=pk)
            choice_text = request.POST.get(choice_id).strip()
            if choice_text == '':
                db_choice.delete()
            else:
                db_choice.text = choice_text
                db_choice.save()
        return redirect('poll', poll_url)
    return TemplateResponse(request, "poll/UniversalChoiceCreation.html", {
        'choices': current_poll.choice_set.all(),
        'poll': current_poll,
        'page': 'Choices',
    })


def values(request, poll_url):
    pass


def delete(request, poll_url):
    """
    :param request:
    :param poll_url: url of poll to be deleted
    :return:

    Given Poll is deleted if delete-button is pressed and if user is authenticated.
    Otherwise the user is directed back to the poll's page.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    error_msg = ""

    if request.method == 'POST':
        if 'Delete' in request.POST:
            if request.user.is_authenticated():
                # TODO restriction for deletion
                return redirect('index')
            else:
                error_msg = "Deletion not allowed. You are not authenticated."
        else:
            return redirect('poll', poll_url)

    return TemplateResponse(request, 'poll/PollDelete.html', {
        'poll': current_poll,
        'error': error_msg,
    })


def vote(request, poll_url):
    """
    :param request:
    :param poll_url: Url of poll
    :return:

    Takes vote with comments as input and saves the vote along with all comments.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        current_vote = Vote(
            date_created=datetime.now(), comment=request.POST.get('comment'),
            poll=current_poll)
        if request.user.is_authenticated():
            current_vote.name = request.user.get_username(),
            current_vote.user = request.user
        else:
            current_vote.name = request.POST.get('name')
            current_vote.anonymous = 'anonymous' in request.POST
        current_vote.save()

        new_choices = []
        for choice in current_poll.choice_set.all():
            if str(choice.id) in request.POST:
                choice_value = get_object_or_404(ChoiceValue, id=request.POST[str(choice.id)])
                new_choices.append(VoteChoice(value=choice_value,
                                              vote=current_vote,
                                              choice=choice,
                                              comment=request.POST['comment_' + str(choice.id)]))
        VoteChoice.objects.bulk_create(new_choices)
        return redirect('poll', poll_url)

    else:
        return TemplateResponse(request, 'poll/VoteCreation.html', {
            'poll': current_poll,
            'matrix': current_poll.get_choice_group_matrix(),
            'choices_matrix': zip(current_poll.get_choice_group_matrix(), current_poll.choice_set.all()),
            'choices': current_poll.choice_set.all(),
            'values': current_poll.choicevalue_set.all(),
            'page': 'Vote',
        })


def vote_assign(request, poll_url, vote_id):
    pass


def vote_edit(request, poll_url, vote_id):
    """
    :param request:
    :param poll_url: Url of Poll belonging to vote
    :param vote_id: ID of vote to be edited
    :return:

    All changes in the given vote are saved.

    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    current_vote = get_object_or_404(Vote, id=vote_id)

    if request.method == 'POST':
        # TODO authentication check
        if request.user.is_anonymous():
            current_vote.name = request.POST['name']
        current_vote.anonymous = 'anonymous' in request.POST
        current_vote.comment = request.POST['comment']

        current_vote.save()

        for choice in current_poll.choice_set.all():
            current_choice = get_object_or_404(VoteChoice, vote=vote_id, choice=choice.id)
            value = get_object_or_404(ChoiceValue, id=request.POST[str(choice.id)])
            current_choice.value = value
            current_choice.comment = request.POST['comment_' + str(choice.id)]

            current_choice.save()

        return redirect('poll', poll_url)

    else:
        vote_choices = []
        for choice in current_poll.choice_set.all():
            vote_choice = get_object_or_404(VoteChoice, vote=vote_id, choice=choice.id)
            vote_choices.append((choice, current_poll.choicevalue_set.all(), vote_choice.comment, vote_choice.value))

        return TemplateResponse(request, 'poll/VoteEdit.html', {
            'poll': current_poll,
            'choices': current_poll.choice_set,
            'values': current_poll.choicevalue_set,
            'vote': current_vote,
            'vote_choices': vote_choices,
            'page': 'Vote',
        })


def vote_delete(request, poll_url, vote_id):
    """
    :param request:
    :param poll_url: url of Poll belonging to vote
    :param vote_id: ID of vote to be deleted
    :return:

    Case Delete:
        If the user is authenticated and is equal to the saved user in the vote, the current vote is deleted.
        The user is redirected to the poll's page.

        If the user is authenticated but not equal to the saved user, the user is directed back with
        error message "Deletion not allowed. You are not [user of vote]".

        If the user is not authenticated, the user is directed back with error message
        "Deletion not allowed. You are not authenticated."

    Case Cancel:
        The user is directed back to the poll's page.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    current_vote = get_object_or_404(Vote, id=vote_id)
    error_msg = ""

    if request.method == 'POST':
        if 'Delete' in request.POST:
            if request.user.is_authenticated():
                # TODO additional possibilities of deleting
                if request.user == current_vote.user:
                    current_vote.delete()
                    return redirect('poll', poll_url)
                else:
                    error_msg = "Deletion not allowed. You are not " + str(current_vote.name) + "."
            else:
                error_msg = "Deletion not allowed. You are not authenticated."
        else:
            return redirect('poll', poll_url)

    return TemplateResponse(request, 'poll/VoteDelete.html', {
        'poll': current_poll,
        'vote': current_vote,
        'error': error_msg,
    })


def copy(request, poll_url):
    """
    :param request:
    :param poll_url: Url of current poll
    :return:

    Takes a new title (optional), a new url (required) and a new due_date (required) as user input.
    Current poll is copied. Title, url and due-date are adapted.
    The new Poll is saved and the user is directed to its page.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)

    if request.method == 'POST':
        form = PollCopyForm(request.POST)
        if form.is_valid():
            choice_values = current_poll.choicevalue_set.all()
            choices = current_poll.choice_set.all()

            current_poll.pk = None
            current_poll.title = form.cleaned_data['title']
            current_poll.url = form.cleaned_data['url']
            current_poll.due_date = form.cleaned_data['due_date']

            current_poll.save()

            for value in choice_values:
                value.pk = None
                value.poll = current_poll
                value.save()

            for choice in choices:
                choice.pk = None
                choice.poll = current_poll
                choice.save()

            return redirect('poll', current_poll.url)

    else:
        form = PollCopyForm({'title': "Copy of" + current_poll.title})

    return TemplateResponse(request, 'poll/Copy.html', {
        'new_Poll': form,
        'poll': poll_url
    })


def transpose(matrix):
    return [list(i) for i in zip(*matrix)]
