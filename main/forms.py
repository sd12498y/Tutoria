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
