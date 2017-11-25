# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-24 14:34
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0011_auto_20171124_2212'),
    ]

    operations = [
        migrations.CreateModel(
            name='myTutor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin', to=settings.AUTH_USER_MODEL)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='admin',
            name='user',
        ),
        migrations.RemoveField(
            model_name='review',
            name='studentID',
        ),
        migrations.RemoveField(
            model_name='review',
            name='tutorID',
        ),
        migrations.AddField(
            model_name='booking',
            name='isReivew',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='review',
            name='bookingID',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to='main.Booking'),
        ),
        migrations.AddField(
            model_name='review',
            name='title',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 24, 14, 34, 19, 133829, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='admin',
        ),
    ]