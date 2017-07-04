from django.dispatch import Signal

class GroupOverview(object):
    pass

show_group_overview = Signal(providing_args=['group', 'members', 'group_dn',
                                             'is_admin', 'is_member'])
