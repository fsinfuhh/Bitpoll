from django.contrib import admin

from .models import Poll, Choice, ChoiceValue, Comment, PollWatch, Vote, VoteChoice


# Register your models here.
admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(ChoiceValue)
admin.site.register(Comment)
admin.site.register(PollWatch)
admin.site.register(Vote)
admin.site.register(VoteChoice)
