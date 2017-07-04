from django.contrib import admin

from mafiasi.groups.models import GroupInvitation, GroupProperties

class GroupPropertiesAdmin(admin.ModelAdmin):
    filter_vertical = ['admins']

admin.site.register(GroupInvitation)
admin.site.register(GroupProperties, GroupPropertiesAdmin)
