# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_invited', models.DateTimeField(default=django.utils.timezone.now)),
                ('group', models.ForeignKey(related_name='invitations', to='auth.Group', on_delete=models.CASCADE)),
                ('invited_by', models.ForeignKey(related_name='given_invitations', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('invitee', models.ForeignKey(related_name='invitations', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupProperties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('public_members', models.BooleanField(default=False)),
                ('admins', models.ManyToManyField(related_name='admin_of', to=settings.AUTH_USER_MODEL)),
                ('group', models.OneToOneField(related_name='properties', to='auth.Group', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
