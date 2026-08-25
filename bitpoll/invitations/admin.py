from django.contrib import admin

from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    raw_id_fields = ('creator', 'user', 'poll', 'vote')