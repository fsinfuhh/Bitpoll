# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0003_auto_20160301_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='due_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='type',
            field=models.CharField(default=b'universal', max_length=20, choices=[(b'universal', b'Universal'), (b'datetime', b'Date-Time'), (b'date', b'Date')]),
        ),
        migrations.AlterField(
            model_name='vote',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='votechoice',
            unique_together=set([('vote_id', 'choice_id')]),
        ),
    ]
