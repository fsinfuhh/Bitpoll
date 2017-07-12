from __future__ import unicode_literals

from django.conf import settings

"""
def create_mafiasi_account(username, email, first_name, last_name, account=None,
                           yeargroup=None, is_student=False, is_guest=False):
    mafiasi = Mafiasi(username=username)
    if first_name and last_name:
        mafiasi.first_name = first_name
        mafiasi.last_name = last_name
    if settings.MAILCLOAK_DOMAIN:
        mafiasi.email = '{}@{}'.format(username, settings.MAILCLOAK_DOMAIN)
    else:
        mafiasi.email = email
    mafiasi.real_email = email
    mafiasi.yeargroup = yeargroup
    mafiasi.is_guest = is_guest
    if account:
        mafiasi.account = account

    return mafiasi
"""