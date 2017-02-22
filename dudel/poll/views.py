import re
from django.contrib import messages
from django.db import transaction

from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.db.models import F, Sum, Count
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from .forms import PollCreationForm, PollCopyForm, DateChoiceCreationForm, UniversalChoiceCreationForm, \
    DTChoiceCreationDateForm, DTChoiceCreationTimeForm
from .models import Poll, Choice, ChoiceValue, Vote, VoteChoice, Comment
from datetime import datetime
from decimal import Decimal


def poll(request, poll_url):
    """
    :param request
    :param poll_url: url of poll

    Displays for a given poll its fields along with all possible choices, all votes and all its comments.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)

    poll_votes = Vote.objects.filter(poll=current_poll).order_by(
        'name').select_related()
    # prefetch_related('votechoice_set').select_releated() #TODO (Prefetch objekt nötig, wie ist der reverse join name wirklich?

    matrix = transpose(current_poll.get_choice_group_matrix())

    # aggregate stats for all columns
    stats = Choice.objects.filter(poll=current_poll).order_by('sort_key').annotate(
        score=Sum('votechoice__value__weight')).values('score', 'id', 'text')
    votes_count = poll_votes.count()
    # aggregate stats for the different Choice_Values per column
    stats2 = Choice.objects.filter(poll=current_poll).order_by('sort_key').annotate(
        count=Count('votechoice__value__color')).values('count', 'id', 'votechoice__value__icon',
                                                        'votechoice__value__color', 'votechoice__value__title')
    #
    # use average for stats
    stats = [{
                 'score': (stat['score'] / Decimal(votes_count) if votes_count > 0 else 0) if stat['score'] is not None else None,
                 'count': stat['score'],
                 'text': stat,
                 'choices': [{'count': stat2['count'], 'color': stat2['votechoice__value__color'],
                              'icon': stat2['votechoice__value__icon'], 'title': stat2['votechoice__value__title']} for
                             stat2 in stats2 if
                             stat2['id'] == stat['id'] and stat2['votechoice__value__color'] != None],
             } for stat in stats]

    return TemplateResponse(request, "poll/poll.html", {
        'poll': current_poll,
        'matrix': matrix,
        'choices_matrix': zip(matrix, current_poll.choice_set.all()),
        'page': '',
        'votes': poll_votes,
        'stats': stats,
        'max_score': max(val['score'] for val in stats if val['score'] is not None) if stats and votes_count > 0 else None,
    })


def comment(request, poll_url):
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        user = None
        if not request.user.is_anonymous:
            user = request.user
        new_comment = Comment(text=request.POST['newCom'],
                              date_created=datetime.now(),
                              name=request.POST['newComName'],
                              poll=current_poll,
                              user=user)
        new_comment.save()
        return redirect('poll', poll_url)
    pass  # todo errorhandling


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
            if request.user.is_authenticated:
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
            for i, datum in enumerate(sorted(form.cleaned_data['dates'].split(","))):
                choice = Choice(text="", date=datum, poll=current_poll, sort_key=i)
                choice.save()
            return redirect('poll', poll_url)
    else:
        form = DateChoiceCreationForm()
    return TemplateResponse(request, "poll/ChoiceCreationDate.html", {
        'poll': current_poll,
        'new_Choice': form,
        'page': 'Choices',
        'is_dt_choice': False,
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
    initial = {
        'dates': ','.join(
            c.date.strftime('%Y-%m-%d')
            for c in current_poll.choice_set.order_by('sort_key')),
        'times': ','.join(set(list(
            c.date.strftime('%H:%M')
            for c in current_poll.choice_set.order_by('sort_key')))),
    }
    form = DTChoiceCreationDateForm(initial=initial)
    if request.method == 'POST':
        form = DTChoiceCreationDateForm(
            request.POST, initial=initial)
        if form.is_valid():
            time = DTChoiceCreationTimeForm(request.POST, initial=initial)
            return TemplateResponse(request, "poll/DTChoiceCreationTime.html", {
                'time': time,
                'poll': current_poll,
                'step': 2,
            })
    return TemplateResponse(request, "poll/ChoiceCreationDate.html", {
        'new_choice': form,
        'poll': current_poll,
        'step': 1,
        'page': 'Choices',
        'is_dt_choice': True,
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
    initial = {
        'dates': ','.join(
            c.date.strftime('%Y-%m-%d')
            for c in current_poll.choice_set.order_by('sort_key')),
        'times': list(set(','.join(
            c.date.strftime('%H:%M')
            for c in current_poll.choice_set.order_by('sort_key')))),
    }
    if request.method == 'POST':
        form = DTChoiceCreationTimeForm(request.POST, initial=initial)
        if form.is_valid():
            times = form.cleaned_data['times'].split(',')
            dates = form.cleaned_data['dates'].split(',')

            return TemplateResponse(request, "poll/DTChoiceCreationCombinations.html", {
                'times': times,
                'dates': dates,
                'poll': current_poll,
            })
        elif form.cleaned_data['dates'] != "":
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
        choice_sort_keys = request.POST.getlist('choice_sort_key')  # TODO: errorhandling
        # TODO: frontend based sorting by user
        for i, choice_text in zip(choice_sort_keys, choice_texts):
            choice_text = choice_text.strip()
            if choice_text == '':
                continue
            choice = Choice(text=choice_text, poll=current_poll, sort_key=i)
            choice.save()

        # update existing choices
        pattern = re.compile(r'^choice_text_(\d+)$')
        with transaction.atomic():
            for choice_id in request.POST.keys():
                choice = pattern.match(choice_id)
                if not choice:
                    continue
                pk = choice.group(1)
                db_choice = get_object_or_404(Choice, poll=current_poll, pk=pk)
                choice_text = request.POST.get(choice_id).strip()
                if choice_text == '':
                    db_choice.delete()  # TODO: nur als gelöscht markieren weil wenn es schon votes gibt, und lehr ignorieren?
                else:
                    db_choice.text = choice_text
                    sort_key = request.POST.get('choice_sort_key_{}'.format(pk), -1)
                    if sort_key == -1:
                        sort_key = current_poll.choice_set.count() + 1  # TODO: unter umständen hier max nemen?
                    db_choice.sort_key = sort_key
                    db_choice.save()
        if 'next' in request.POST:
            return redirect('poll', poll_url)
    return TemplateResponse(request, "poll/UniversalChoiceCreation.html", {
        'choices': current_poll.choice_set.all().order_by('sort_key'),
        'poll': current_poll,
        'page': 'Choices',
        'next_sort_key': current_poll.choice_set.count() + 1,  # TODO: unter umständen hier max nemen?
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
            if request.user.is_authenticated:
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


def vote(request, poll_url, vote_id=None):
    """
    :param request:
    :param poll_url: Url of poll
    :param vote_id: Optional the voteID to edit
    :return:

    Takes vote with comments as input and saves the vote along with all comments.
    """
    current_poll = get_object_or_404(Poll, url=poll_url)
    if request.method == 'POST':
        vote_id = request.POST.get('vote_id', None)
        if vote_id:
            current_vote = get_object_or_404(Vote, pk=vote_id, poll=current_poll)
            if not current_vote.can_edit(request.user):
                # the vote belongs to an user and it is not the authenticated user
                return HttpResponseForbidden()  # todo: better errorpage?
        else:
            current_vote = Vote(poll=current_poll)
        current_vote.date_created = datetime.now()
        current_vote.comment = request.POST.get('comment')
        if vote_id:
            # leave the name as it was
            pass
        elif request.user.is_authenticated:
            current_vote.name = request.user.get_username()
            current_vote.user = request.user
        else:
            current_vote.name = request.POST.get('name').strip()
        current_vote.anonymous = 'anonymous' in request.POST

        if current_vote.anonymous or current_vote.name:
            # prevent non-anonymous vote without name

            with transaction.atomic():
                new_choices = []

                current_vote.save()

                for choice in current_poll.choice_set.all():
                    if str(choice.id) in request.POST:
                        choice_value = get_object_or_404(ChoiceValue, id=request.POST[str(choice.id)])
                    else:
                        choice_value = None
                    new_choices.append(VoteChoice(value=choice_value,
                                                  vote=current_vote,
                                                  choice=choice,
                                                  comment=request.POST.get('comment_{}'.format(choice.id)) or ''))
                if vote_id:
                    VoteChoice.objects.filter(vote=current_vote).delete()
                    #todo: nochmal prüfen ob das wirjklich das tut was es soll, also erst alles löschen und dann neu anlegen
                    #todo eventuell eine transaktion drum machen? wegen falls das eventuell dazwischen abbricht?
                VoteChoice.objects.bulk_create(new_choices)

                return redirect('poll', poll_url)
        else:
            messages.error(
                request, _('You need to either provide a name or post an anonymous vote.'))

    # no/invalid POST: show the dialog
    matrix = current_poll.get_choice_group_matrix()
    choices = []
    comments = []
    choice_votes = []
    if vote_id:
        current_vote = get_object_or_404(Vote, pk=vote_id)
    else:
        current_vote = Vote()
    if current_poll.type == 'normal':
        choices_orig = current_poll.choice_set.all().order_by('sort_key')
    else:
        choices_orig = current_poll.choice_set.all()
    for choice in choices_orig:
        cur_comment = ""
        value = None
        if request.method == 'POST':
            if str(choice.id) in request.POST:
                value = get_object_or_404(ChoiceValue, id=request.POST[str(choice.id)])
            else:
                value = None
            cur_comment = request.POST.get('comment_{}'.format(choice.id)) or ''
        elif vote_id:  # If we want to edit an vote find the selected fields
            vote_choice = VoteChoice.objects.filter(vote=vote_id, choice=choice.id)
            if vote_choice:  # append the found values
                cur_comment = vote_choice[0].comment
                value = vote_choice[0].value
        choices.append(choice)
        comments.append(cur_comment)
        choice_votes.append(value)
    return TemplateResponse(request, 'poll/VoteCreation.html', {
        'poll': current_poll,
        'matrix': matrix,
        'matrix_len': len(matrix[0]),
        'choices_matrix': zip(matrix, choices, comments, choice_votes),
        'choices': current_poll.choice_set.all(),
        'choices_matrix_len': len(choices),
        'values': current_poll.choicevalue_set.all(),
        'page': 'Vote',
        'current_vote': current_vote,
    })


def vote_assign(request, poll_url, vote_id):
    pass


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
            if request.user.is_authenticated:
                # TODO additional possibilities of deleting
                if current_vote.can_delete(request.user):
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
