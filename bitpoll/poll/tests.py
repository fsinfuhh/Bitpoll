from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from bitpoll.base.models import BitpollUser
from bitpoll.poll.models import Poll, PollWatch, Vote


class CanWatchTestCase(TestCase):
    """Tests for Poll.can_watch() logic."""

    def setUp(self):
        self.owner = BitpollUser.objects.create_user(
            username='owner', password='testpass123'
        )
        self.other_user = BitpollUser.objects.create_user(
            username='other', password='testpass123'
        )
        self.poll = Poll.objects.create(
            title='Test Poll',
            url='test-poll',
            type='universal',
            user=self.owner,
            show_results='complete',
        )

    def test_owner_can_always_watch(self):
        """Owner can watch regardless of show_results setting."""
        for results_setting, _ in Poll._meta.get_field('show_results').choices:
            self.poll.show_results = results_setting
            self.poll.save()
            self.assertTrue(
                self.poll.can_watch(self.owner),
                f"Owner should be able to watch when show_results='{results_setting}'"
            )

    def test_user_can_watch_when_results_complete(self):
        self.poll.show_results = 'complete'
        self.poll.save()
        self.assertTrue(self.poll.can_watch(self.other_user))

    def test_user_can_watch_when_results_summary(self):
        self.poll.show_results = 'summary'
        self.poll.save()
        self.assertTrue(self.poll.can_watch(self.other_user))

    def test_user_cannot_watch_when_results_never(self):
        self.poll.show_results = 'never'
        self.poll.save()
        self.assertFalse(self.poll.can_watch(self.other_user))

    def test_user_cannot_watch_when_results_summary_after_vote(self):
        self.poll.show_results = 'summary after vote'
        self.poll.save()
        self.assertFalse(self.poll.can_watch(self.other_user))

    def test_user_cannot_watch_when_results_complete_after_vote(self):
        self.poll.show_results = 'complete after vote'
        self.poll.save()
        self.assertFalse(self.poll.can_watch(self.other_user))

    def test_voted_user_can_watch_summary_after_vote(self):
        self.poll.show_results = 'summary after vote'
        self.poll.save()
        Vote.objects.create(
            name='other', user=self.other_user, poll=self.poll,
            date_created=timezone.now(), comment='',
        )
        self.assertTrue(self.poll.can_watch(self.other_user))

    def test_voted_user_cannot_watch_when_never(self):
        self.poll.show_results = 'never'
        self.poll.save()
        Vote.objects.create(
            name='other', user=self.other_user, poll=self.poll,
            date_created=timezone.now(), comment='',
        )
        self.assertFalse(self.poll.can_watch(self.other_user))


class WatchViewTestCase(TestCase):
    """Tests for the watch/unwatch view."""

    def setUp(self):
        self.owner = BitpollUser.objects.create_user(
            username='owner', password='testpass123'
        )
        self.other_user = BitpollUser.objects.create_user(
            username='other', password='testpass123'
        )
        self.poll = Poll.objects.create(
            title='Test Poll',
            url='test-poll',
            type='universal',
            user=self.owner,
            show_results='complete',
        )
        self.watch_url = reverse('poll_watch', args=['test-poll'])
        self.client = Client()

    def test_watch_requires_login(self):
        response = self.client.post(self.watch_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_watch_requires_post(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(self.watch_url)
        self.assertEqual(response.status_code, 405)

    def test_user_can_watch_poll(self):
        self.client.login(username='other', password='testpass123')
        self.client.post(self.watch_url)
        self.assertTrue(
            PollWatch.objects.filter(poll=self.poll, user=self.other_user).exists()
        )

    def test_user_can_unwatch_poll(self):
        PollWatch.objects.create(poll=self.poll, user=self.other_user)
        self.client.login(username='other', password='testpass123')
        self.client.post(self.watch_url)
        self.assertFalse(
            PollWatch.objects.filter(poll=self.poll, user=self.other_user).exists()
        )

    def test_unwatch_allowed_when_results_changed_to_never(self):
        """The main bug: user watches, then results set to 'never', unwatch must still work."""
        PollWatch.objects.create(poll=self.poll, user=self.other_user)
        self.poll.show_results = 'never'
        self.poll.save()

        self.client.login(username='other', password='testpass123')
        self.client.post(self.watch_url)
        self.assertFalse(
            PollWatch.objects.filter(poll=self.poll, user=self.other_user).exists()
        )

    def test_watch_denied_when_results_never(self):
        """User cannot subscribe to watch when results are 'never'."""
        self.poll.show_results = 'never'
        self.poll.save()

        self.client.login(username='other', password='testpass123')
        self.client.post(self.watch_url)
        self.assertFalse(
            PollWatch.objects.filter(poll=self.poll, user=self.other_user).exists()
        )

    def test_owner_can_watch_when_results_never(self):
        self.poll.show_results = 'never'
        self.poll.save()

        self.client.login(username='owner', password='testpass123')
        self.client.post(self.watch_url)
        self.assertTrue(
            PollWatch.objects.filter(poll=self.poll, user=self.owner).exists()
        )

    def test_owner_can_unwatch_when_results_never(self):
        PollWatch.objects.create(poll=self.poll, user=self.owner)
        self.poll.show_results = 'never'
        self.poll.save()

        self.client.login(username='owner', password='testpass123')
        self.client.post(self.watch_url)
        self.assertFalse(
            PollWatch.objects.filter(poll=self.poll, user=self.owner).exists()
        )
