# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-26 13:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_auto_20171126_2052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mytutor',
            name='admin',
        ),
        migrations.RemoveField(
            model_name='mytutor',
            name='staff',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 26, 13, 0, 25, 190891, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='myTutor',
        ),
    ]
