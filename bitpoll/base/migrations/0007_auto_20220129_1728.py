# Generated by Django 2.2.17 on 2022-01-29 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20180704_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bitpolluser',
            name='displayname',
            field=models.CharField(default='', max_length=100),
        ),
    ]