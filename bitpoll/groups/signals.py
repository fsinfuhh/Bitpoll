from django.dispatch import Signal

class GroupOverview(object):
    pass

show_group_overview = Signal(providing_args=['group', 'members',
                                             'is_admin', 'is_member'])
