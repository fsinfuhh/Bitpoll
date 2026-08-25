from django.contrib import admin

from .models import Poll, Choice, ChoiceValue, Comment, PollWatch, Vote, VoteChoice


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'user', 'created')
    search_fields = ('title', 'url', 'user__username')
    raw_id_fields = ('user', 'group')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'poll', 'user', 'date_created')
    search_fields = ('text', 'name', 'user__username', 'poll__title')
    raw_id_fields = ('poll', 'user')


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    raw_id_fields = ('poll',)


@admin.register(ChoiceValue)
class ChoiceValueAdmin(admin.ModelAdmin):
    raw_id_fields = ('poll',)


@admin.register(PollWatch)
class PollWatchAdmin(admin.ModelAdmin):
    raw_id_fields = ('poll', 'user')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'poll', 'assigned_by')


@admin.register(VoteChoice)
class VoteChoiceAdmin(admin.ModelAdmin):
    raw_id_fields = ('value', 'vote', 'choice')
