import psycopg2
import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from dudel.poll.models import Choice, ChoiceValue, Comment, Poll, Vote, VoteChoice


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
        conn_string = "host='{}' dbname='{}' user='{}' password='{}'".format(
            options['db_host'], options['db_name'], options['db_user'], options['db_password'])

        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # migrating polls
        migrated_polls = set()
        choices = {}
        choice_values = {}
        print('migrating polls')
        cursor.execute('SELECT * FROM poll WHERE deleted=false;')
        for poll in cursor:
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
            local_poll = Poll.objects.filter(url=poll['slug'])
            if local_poll.count() > 0:
                # poll exists.
                continue
            migrated_poll = Poll(
                title=poll['title'],
                description=poll['description'],
                url=poll['slug'],
                type=POLL_TYPE_MAPPING[poll['type']],
                created=timezone.localize(poll['created']),
                due_date=timezone.localize(poll['due_date']) if poll['due_date'] is not None else None,
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

            if poll['owner_id'] and poll['owner_id'] > 0:
                # group owner
                migrated_poll.user = self.resolve_user(poll['owner_id'])
            elif poll['owner_id'] and poll['owner_id'] < 0:
                # user owner
                migrated_poll.user = self.resolve_group(-poll['owner_id'])
            
            migrated_poll.save()
            migrated_polls.add((poll['id'], migrated_poll))

        # migrating choice values and choices
        print('Migrating comments, choice values, choices and votes for previously imported polls')
        for poll_id, poll in migrated_polls:
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
                    date=timezone.localize(choice['date']) if choice['date'] else None,
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
                    date_created=timezone.localize(vote['created']),
                    comment=vote['comment'],
                    assigned_by=self.resolve_user(vote['assigned_by_id']) if vote['assigned_by_id'] else None,
                    poll=poll,
                    user=self.resolve_user(vote['user_id']) if vote['user_id'] else None)
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
                    date_created=timezone.localize(comment['created']),
                    name=comment['name'] or '',
                    user=self.resolve_user(comment['user_id']),
                    poll=poll)

    @staticmethod
    def resolve_user(old_user_id):
        """Resolve a user by its user id from old dudel."""
        # TODO: do actual resolving
        return get_user_model().objects.first()

    @staticmethod
    def resolve_group(old_group_id):
        """Resolve a group by its id from old dudel."""
        # TODO: do actual resolving
        return Group.objects.first()
