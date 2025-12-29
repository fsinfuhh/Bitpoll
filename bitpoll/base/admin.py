from django.contrib import admin

from bitpoll.base.models import BitpollUser

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm


class BitpollUserChangeForm(UserChangeForm):
    class Meta:
        model = BitpollUser
        fields = '__all__'


class BitpollUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {'fields': ('language', 'email_invitation', 'timezone', 'auto_watch', 'displayname')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional info', {'fields': ('language', 'email_invitation', 'timezone', 'auto_watch', 'displayname')}),
    )
    form = BitpollUserChangeForm


admin.site.register(BitpollUser, BitpollUserAdmin)
