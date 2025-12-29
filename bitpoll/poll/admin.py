from django.contrib import admin

from .models import Poll, Choice, ChoiceValue, Comment, PollWatch, Vote, VoteChoice


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'user', 'created')
    search_fields = ('title', 'url', 'user__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'poll', 'user', 'date_created')
    search_fields = ('text', 'name', 'user__username', 'poll__title')


admin.site.register(Choice)
admin.site.register(ChoiceValue)
admin.site.register(PollWatch)
admin.site.register(Vote)
admin.site.register(VoteChoice)
