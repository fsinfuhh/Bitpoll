import psycopg2
import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware
import sys

from bitpoll.poll.models import Choice, ChoiceValue, Comment, Poll, Vote, VoteChoice


POLL_TYPE_MAPPING = {
    'normal': 'universal',
    'day': 'date',
    'date': 'datetime',
}


class Command(BaseCommand):
    help = 'Import data from the old dudel.'

    def add_arguments(self, parser):
        parser.add_argument('db_host', type=str)
        parser.add_argument('db_name', type=str)
        parser.add_argument('db_user', type=str)
        parser.add_argument('db_password', type=str)

    def handle(self, *args, **options):
        """Import data from the old dudel."""
        # connect to db
        self.conn_string = "host='{}' dbname='{}' user='{}' password='{}'".format(
            options['db_host'], options['db_name'], options['db_user'], options['db_password'])

        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()

        # migrating polls
        print('migrating polls')
        count = 0
        cursor.execute('SELECT COUNT(*) FROM poll WHERE deleted=false')
        total_count = cursor.fetchone()[0]
        migrated_polls = set()
        choices = {}
        choice_values = {}
        cursor.execute('SELECT * FROM poll WHERE deleted=false;')
        for poll in cursor:
            sys.stdout.write('\r{:4d}/{:4d} polls migrated'.format(count, total_count))
            sys.stdout.flush()
            count += 1

            poll = {
                'id': poll[0],
                'title': poll[1],
                'description': poll[2] or '',
                'slug': poll[3],
                'type': poll[4],
                'created': poll[5],
                'owner_id': poll[6],
                'due_date': poll[7],
                'anonymous_allowed': poll[8],
                'public_listing': poll[9],
                'require_login': poll[10],
                'show_results': poll[11],
                'send_mail': poll[12],
                'one_vote_per_user': poll[13],
                'allow_comments': poll[14],
                'deleted': poll[15],
                'require_invitation': poll[16] or False,
                'show_invitations': poll[17] or True,
                'timezone_name': poll[18] or 'Europe/Berlin',
            }
            timezone = pytz.timezone(poll['timezone_name'])
            local_poll = Poll.objects.filter(url=poll['slug']).first()

            new_pk = None
            if local_poll:
                # poll exists. Delete it to get rid of related elements
                new_pk = local_poll.pk
                local_poll.delete()

            created = make_aware(poll['created'], timezone)
            migrated_poll = Poll(
                title=poll['title'],
                description=poll['description'],
                url=poll['slug'],
                type=POLL_TYPE_MAPPING[poll['type']],
                due_date=make_aware(poll['due_date'], timezone) if poll['due_date'] is not None else None,
                anonymous_allowed=poll['anonymous_allowed'],
                public_listening=poll['public_listing'],
                require_login=poll['require_login'],
                require_invitation=poll['require_invitation'],
                show_results=poll['show_results'],
                send_mail=poll['send_mail'],
                one_vote_per_user=poll['one_vote_per_user'],
                allow_comments=poll['allow_comments'],
                show_invitations=poll['show_invitations'],
                timezone_name=poll['timezone_name'])
            migrated_poll.pk = new_pk

            owner = self.resolve_user_or_group(poll['owner_id'])
            if isinstance(owner, get_user_model()):
                # user owner
                migrated_poll.user = owner
            elif isinstance(owner, Group):
                # group owner
                migrated_poll.group = owner
            
            migrated_poll.save()
            migrated_poll.created = created
            migrated_poll.save()
            migrated_polls.add((poll['id'], migrated_poll))
        sys.stdout.write('\n')

        # migrating choice values and choices
        print('migrating comments, choice values, choices and votes for previously imported polls')
        count = 0
        total_count = len(migrated_polls)
        for poll_id, poll in migrated_polls:
            sys.stdout.write('\r{:4d}/{:4d} polls handled'.format(count, total_count))
            sys.stdout.flush()
            count += 1

            # nothing to delete, poll has just been created.

            timezone = pytz.timezone(poll.timezone_name)

            # choices
            cursor.execute('SELECT * FROM choice WHERE deleted=false AND poll_id=%s ORDER BY date, text;', (poll_id,))
            sort_key = 0
            for choice in cursor:
                choice = {
                    'id': choice[0],
                    'text': choice[1] or '',
                    'date': choice[2],
                    'poll_id': choice[3],
                    'deleted': choice[4],
                }
                c = Choice.objects.create(
                    text=choice['text'],
                    date=make_aware(choice['date'], timezone) if choice['date'] else None,
                    poll=poll,
                    sort_key=sort_key,
                    deleted=choice['deleted'])
                choices[choice['id']] = c
                sort_key += 1

            # choice values
            cursor.execute('SELECT * FROM choice_value WHERE deleted=false AND poll_id=%s;', (poll_id,))
            for choice_value in cursor:
                choice_value = {
                    'id': choice_value[0],
                    'title': choice_value[1],
                    'icon': choice_value[2],
                    'color': choice_value[3],
                    'poll_id': choice_value[4],
                    'deleted': choice_value[5],
                    'weight': choice_value[6],
                }
                c = ChoiceValue.objects.create(
                    title=choice_value['title'],
                    icon=choice_value['icon'],
                    color=choice_value['color'],
                    weight=choice_value['weight'],
                    poll=poll)
                choice_values[choice_value['id']] = c

            # vote
            cursor.execute('SELECT * FROM vote WHERE poll_id=%s;', (poll_id,))
            votes_migrated = set()
            for vote in cursor:
                vote = {
                    'id': vote[0],
                    'name': vote[1] or '',
                    'poll_id': vote[2],
                    'user_id': vote[3],
                    'anonymous': vote[4],
                    'created': vote[5],
                    'comment': vote[6],
                    'assigned_by_id': vote[7],
                }
                v = Vote.objects.create(
                    name=vote['name'],
                    anonymous=vote['anonymous'],
                    date_created=make_aware(vote['created'], timezone),
                    comment=vote['comment'],
                    assigned_by=self.resolve_user_or_group(vote['assigned_by_id']) if vote['assigned_by_id'] else None,
                    poll=poll,
                    user=self.resolve_user_or_group(vote['user_id']) if vote['user_id'] else None)
                votes_migrated.add((vote['id'], v))
            for vote_id, vote in votes_migrated:
                # vote choices
                cursor.execute('SELECT * FROM vote_choice WHERE vote_id=%s;', (vote_id,))
                for vote_choice in cursor:
                    vote_choice = {
                        'id': vote_choice[0],
                        'comment': vote_choice[1],
                        'value_id': vote_choice[2],
                        'vote_id': vote_choice[3],
                        'choice_id': vote_choice[4],
                    }
                    try:
                        VoteChoice.objects.create(
                            comment=vote_choice['comment'],
                            value=choice_values[vote_choice['value_id']] if vote_choice['value_id'] else None,
                            vote=vote,
                            choice=choices[vote_choice['choice_id']] if vote_choice['choice_id'] else None)
                    except (KeyError, IntegrityError):
                        continue

            # comments
            cursor.execute('SELECT * FROM comment WHERE poll_id=%s AND deleted=false;', (poll_id,))
            for comment in cursor:
                comment = {
                    'id': comment[0],
                    'text': comment[1],
                    'created': comment[2],
                    'name': comment[3],
                    'user_id': comment[4],
                    'poll_id': comment[5],
                    'deleted': comment[6],
                }
                Comment.objects.create(
                    text=comment['text'],
                    date_created=make_aware(comment['created'], timezone),
                    name=comment['name'] or '',
                    user=self.resolve_user_or_group(comment['user_id']),
                    poll=poll)
        sys.stdout.write('\n')

        print('Finished.')

    def resolve_user_or_group(self, old_id):
        """Resolve a user by its user id from old dudel."""
        # connect to db
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()

        cursor.execute('SELECT username FROM "user" WHERE id=%s', (old_id,))
        username = cursor.fetchone()
        try:
            if username:
                return get_user_model().objects.get(username=username[0])
            else:
                cursor.execute('SELECT name FROM "group" WHERE id=%s', (old_id,))
                groupname = cursor.fetchone()
                if groupname:
                    return Group.objects.get(name=groupname[0])
        except ObjectDoesNotExist:
            return None
