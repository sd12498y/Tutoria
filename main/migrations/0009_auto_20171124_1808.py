# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-24 10:08
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20171124_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutor',
            name='isactivated',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 24, 10, 8, 13, 685048, tzinfo=utc)),
        ),
    ]
