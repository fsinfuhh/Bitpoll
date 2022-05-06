import random
import time
from typing import Dict, Tuple

from django.conf import settings as django_settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature
from django.utils.translation import gettext_lazy as _


def create_anti_spam_challenge(poll_id: int) -> Dict:
    """Creates a anti spam challenge"""
    rand = random.SystemRandom()
    x = rand.randint(1, 10)
    y = rand.randint(1, 10)
    op = rand.choice(['+', '-', '*'])
    return {'key': signing.dumps({
                'type': 'anti_spam',
                'x': x,
                'y': y,
                'op': op,
                'poll_id': poll_id,
                'time': time.time()
            }),
        'x': x,
        'y': y,
        'op': op,
    }


def get_spam_challenge_from_key(key: str, poll_id: int) -> Dict:
    """Returns the anti spam challenge from the key, or generates a new if it is not valid"""
    try:
        spam_data = signing.loads(key)
        if spam_data.get('type') != 'anti_spam' or spam_data['time'] <= time.time() - django_settings.ANTI_SPAM_CHALLENGE_TTL:
            return create_anti_spam_challenge(poll_id)
        spam_data['key'] = key
        return spam_data
    except BadSignature:
        return create_anti_spam_challenge(poll_id)


def check_anti_spam_challange(key: str, answer: str, poll_id: int) -> bool:
    """Checks if the anti spam cheallenge was solved and not expired"""
    try:
        spam_data = signing.loads(key)
        if spam_data.get('type') != 'anti_spam':
            raise ValidationError(_("Error while checking response"))
    except BadSignature:
        raise ValidationError(_("Error while checking response"))
    if spam_data['poll_id'] != poll_id:
        raise ValidationError(_("Error while checking response"))
    if spam_data['time'] <= time.time() - django_settings.ANTI_SPAM_CHALLENGE_TTL:
        raise ValidationError(_("Question Expired, please solve the new question."))
    if answer is None:
        raise ValidationError(_('Field is required'))
    op = spam_data['op']
    x = spam_data['x']
    y = spam_data['y']

    if op == '+':
        return answer == x + y
    if op == '-':
        return answer == x - y
    if op == '*':
        return answer == x * y
    raise ValidationError(_("Error while checking response"))
