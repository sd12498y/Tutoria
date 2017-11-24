from django import forms
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Booking
from django.forms import extras

class SessionForm(forms.Form):
    #days = forms.ModelChoiceField(queryset=Booking.objects.all().order_by('Bookingid'))
    SessionDate = forms.DateField(label='Which Date?', required=True)
    StartTime = forms.TimeField(label='Start Time?', required=True)
    EndTime = forms.TimeField(label='End Time?', required=True)

class StudentRegisterForm(forms.Form):
	firstName = forms.CharField()
	lastName = forms.CharField()
	tel = forms.CharField()
	email = forms.EmailField()
	username = forms.CharField()
	password1 = forms.CharField()
	password2 = forms.CharField()
	image = forms.FileField(required=False)
	school = forms.CharField()

class TutorRegisterForm(forms.Form):
	firstName = forms.CharField()
	lastName = forms.CharField()
	tel = forms.CharField()
	email = forms.EmailField()
	username = forms.CharField()
	password1 = forms.CharField()
	password2 = forms.CharField()
	image = forms.FileField(required=False)
	school = forms.CharField()
	description = forms.CharField()
	type = forms.CharField()
	hourly_rate = forms.FloatField()

class BothRegisterForm(forms.Form):
	firstName = forms.CharField()
	lastName = forms.CharField()
	tel = forms.CharField()
	email = forms.EmailField()
	username = forms.CharField()
	password1 = forms.CharField()
	password2 = forms.CharField()
	image = forms.FileField(required=False)
	school1 = forms.CharField()
	school2 = forms.CharField()
	description = forms.CharField()
	type = forms.CharField()
	hourly_rate = forms.FloatField()
