# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-24 20:05
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20171125_0315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 24, 20, 5, 30, 86504, tzinfo=utc)),
        ),
    ]
