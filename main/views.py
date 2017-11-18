# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
from datetime import datetime, date, time, timedelta
from django.shortcuts import render, render_to_response
from django.views import generic
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import myUser, Tutor, Booking, Transaction, Wallet, Session
from django.db.models import Q
from notifications.signals import notify
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from dateutil.rrule import *
from dateutil.parser import *
from dateutil import rrule
from datetime import *
from django.template import loader
from django.utils import timezone
import pprint
import sys
from .forms import SessionForm
# Create your views here.

def login(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('main:index'))
	else:
		return HttpResponseRedirect('/login/')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def index(request):
    return render_to_response('index.html',locals())

class WalletView(generic.ListView):
    template_name = 'wallet.html'
    context_object_name = 'transaction_history'
    def get_queryset(self):
        """Return the last five published questions."""
        return self.request.user.myuser.wallet.getHistory()
def addValue(request):
	request.user.myuser.wallet.addValue(100)
	return HttpResponseRedirect(reverse('main:wallet'))

class BookingHistoryView(generic.ListView):
    template_name = 'booking_history.html'
    context_object_name = 'booking_history'
    def get_queryset(self):
        """Return the last five published questions."""
        return Booking.objects.filter(Q(student=self.request.user.myuser) | Q(tutor=self.request.user.myuser) ).order_by('-timestamp')[:7]

class SearchResultView(generic.ListView):
	template_name = 'searchResults.html'
	context_object_name = 'ListOfTutor'
	def get_queryset(self):
		return Tutor.objects.all()
'''
class BioView(generic.DetailView):
	model = Tutor
	template_name = 'bio.html'
'''
def bio(request, TutorID):
   
    
    TargetTutor = Tutor.objects.get(pk = TutorID)
    BookSessionOfTutor = Booking.objects.filter(tutor = TargetTutor.user)
    
    Dates = []
    TodayDate = timezone.now().date()
    StartDate = TodayDate - timedelta(days=TodayDate.weekday())
    EndDate = StartDate + timedelta(days=6)
    Dates.append(EndDate)
    
    for n in range(int((EndDate - StartDate).days)):
        TempDay = StartDate + timedelta(n)
        Dates.append(TempDay)
    
    now = timezone.now()
    sevenDaysLater = now + timedelta(days=7)
    
    ListOfSessions = []
    Hours = []
    found = 0
    appendonce = 0
    
    #for each date
    for eachdate in Dates:
        #print eachdate
        DateBookSessionOfTutor = Booking.objects.filter(tutor = TargetTutor.user, session_date = eachdate)
        
        #for each hour
        for smoketest in rrule.rrule(rrule.HOURLY, dtstart=TodayDate, count=24):
            eachhour = smoketest.strftime('%H:%M:%S')
            if not any(eachhour in s for s in Hours):
                Hours.append(eachhour)
            
            #print smoketest
            found = 0
            tempbuttonid = eachdate.strftime('%Y%m%d') + smoketest.strftime('%H%M%S')
            for x in DateBookSessionOfTutor:
                
                #string of Booked starttime of that tutor on that date
                strx = x.start_time.strftime('%H:%M:%S')
               
                if strx == eachhour:
                    #print "yes"
                    found = 1
                    tempsession = Session(eachdate, eachhour, (smoketest+timedelta(hours=1)), "Booked", eachhour, tempbuttonid)
                
            if found == 0:
                tempsession = Session(eachdate, eachhour, (smoketest+timedelta(hours=1)), "Free", eachhour, tempbuttonid)
                
            ListOfSessions.append(tempsession)
    
    template = loader.get_template('bio.html')
    Sform = SessionForm()
    context = {'TargetTutor': TargetTutor, 'TodayDate': TodayDate, 'StartDate': StartDate, "EndDate": EndDate, "Dates": Dates, "Times": Hours, "ListOfSessions": ListOfSessions, 'Sform': Sform, }
    return HttpResponse(template.render(context, request))


def confirmBooking(request, TutorID):
	t = Tutor.objects.get(pk=TutorID)
	if request.method=="POST":
		Sform = SessionForm(request.POST)
		if Sform.is_valid():
			SFormData = Sform.cleaned_data
			date=SFormData['SessionDate']
			start=SFormData['StartTime']
			end=SFormData['EndTime']
			b = Booking(session_date=date, student=request.user.myuser,tutor=t.user, start_time=start, end_time=end, tutoring_fee=t.hourly_rate, commission=t.hourly_rate*0.05, total_payable=t.hourly_rate+t.hourly_rate*0.05)
			b.save()
			w = Wallet.objects.get(user=request.user.myuser)
			w.balance -= t.hourly_rate+t.hourly_rate*0.05
			w.save()
			t = Transaction(payer=request.user.myuser , receiver=t.user, amount=t.hourly_rate+t.hourly_rate*0.05, action="Outgoing Payment")
			t.save()
			send_mail(
		    'Your session has been booked',
		    'Booking details.',
		    'system@solveware.com',
		    ['tutor@gmail.com'],
		    fail_silently=False,
			)
			send_mail(
		    'Your session has successfully been booked',
		    'Booking details.',
		    'system@solveware.com',
		    ['student@gmail.com'],
		    fail_silently=False,
			)
			return HttpResponseRedirect(reverse('main:bookingDetail', args=(b.id,)))
		else:
			return HttpResponse('<p>error</p>')

class CancelView(generic.DetailView):
	model = Booking
	template_name = 'cancel.html'


def ConfirmCancel(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = "Cancelled"
    booking.save()
    wallet = get_object_or_404(Wallet, user=booking.student)
    wallet.refund(booking.total_payable, booking.tutor)

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('main:bookingHistory'))


class BookingDetailView(generic.DetailView):
	template_name = 'booking_details.html'
	model = Booking
	''' 
    #FromBooked = False
    #if it is redirected from confirmbooking, meaning the booking is just made
    #if request.session.get('BookingData_token') == True:
       # FromBooked = True
    #if it is redirected from confirmbooking, meaning the booking is just made
    #cant make at this moment
    #FromBooked = False
    
    BookingData = Booking.objects.get(Bookingid = BookingID)
    
    template = loader.get_template('tutor/BookingDetails.html')
    context = {'BookingData': BookingData, 'FromBooked': FromBooked,}
    return HttpResponse(template.render(context, request))
    '''


