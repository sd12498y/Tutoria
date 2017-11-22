# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-22 18:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_auto_20171123_0039'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('totalPayable', models.FloatField()),
                ('bookingID', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='p_bookingID', to='main.Booking')),
                ('receiverID', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='p_receiverID', to=settings.AUTH_USER_MODEL)),
                ('senderID', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='p_senderID', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
