from django.contrib import admin

from dudel.base.models import DudelUser

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm


class DudelUserChangeForm(UserChangeForm):
    class Meta:
        model = DudelUser
        fields = '__all__'


class DudelUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {'fields': ('language', 'email_invitation', 'timezone', 'auto_watch')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional info', {'fields': ('language', 'email_invitation', 'timezone', 'auto_watch')}),
    )
    form = DudelUserChangeForm

admin.site.register(DudelUser)
