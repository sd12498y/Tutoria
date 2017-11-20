# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-20 17:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sessionDate', models.DateField()),
                ('startTime', models.TimeField()),
                ('endTime', models.TimeField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('tutoringFee', models.FloatField(default=0, null=True)),
                ('totalPayable', models.FloatField(default=0, null=True)),
                ('commission', models.FloatField(default=0, null=True)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CouponCode', models.CharField(default='', max_length=10)),
                ('startDateTime', models.DateTimeField(default=django.utils.timezone.now)),
                ('endDateTime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CourseCatalogue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courseCode', models.CharField(default='', max_length=8)),
                ('courseName', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='myUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tel', models.CharField(max_length=8)),
                ('profilePicture', models.FileField(upload_to='img/propic/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('rate', models.FloatField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SessionDate', models.DateField(blank=True, null=True)),
                ('StartTime', models.TimeField(blank=True, null=True)),
                ('EndTime', models.TimeField(blank=True, null=True)),
                ('Status', models.CharField(default='DEFAULTSTATUS', max_length=30)),
                ('Buttonid', models.CharField(default='00000000000000', max_length=14)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('university', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.myUser')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('transactionAmount', models.FloatField()),
                ('action', models.CharField(choices=[('Add Value', 'Add Value'), ('Refund', 'Refund'), ('Tutorial Payment', 'Tutorial Payment')], max_length=30)),
                ('bookingID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Booking')),
                ('receiverID', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='receiverID', to=settings.AUTH_USER_MODEL)),
                ('senderID', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='senderID', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('university', models.CharField(max_length=50)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContractTutor',
            fields=[
                ('tutor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.Tutor')),
                ('ContractID', models.CharField(default='', max_length=30)),
            ],
            bases=('main.tutor',),
        ),
        migrations.CreateModel(
            name='PrivateTutor',
            fields=[
                ('tutor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.Tutor')),
                ('hourlyRate', models.FloatField(default=0, null=True)),
            ],
            bases=('main.tutor',),
        ),
        migrations.AddField(
            model_name='tutor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.myUser'),
        ),
        migrations.AddField(
            model_name='tag',
            name='tutorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Tutor'),
        ),
        migrations.AddField(
            model_name='review',
            name='studentID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='r_student', to='main.Student'),
        ),
        migrations.AddField(
            model_name='review',
            name='tutorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='r_tutor', to='main.Tutor'),
        ),
        migrations.AddField(
            model_name='course',
            name='courseCode',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='CC_CourseCode', to='main.CourseCatalogue'),
        ),
        migrations.AddField(
            model_name='course',
            name='tutorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Tutor'),
        ),
        migrations.AddField(
            model_name='booking',
            name='studentID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='b_student', to='main.myUser'),
        ),
        migrations.AddField(
            model_name='booking',
            name='tutorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='b_tutor', to='main.myUser'),
        ),
    ]
