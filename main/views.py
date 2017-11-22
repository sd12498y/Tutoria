# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import json
from datetime import datetime, date, time, timedelta
from django.shortcuts import render, render_to_response
from django.views import generic
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import myUser, Tutor, PrivateTutor, ContractTutor, Booking, Transaction, Wallet, Session, Course, Coupon
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
from django.utils.timezone import localtime
import pprint
import sys
from .forms import SessionForm

#Olivia: 7/11/17 14:50
from django.db.models import Q
import pytz

from django.core import serializers

# Create your views here.

def getCommissionRate():
    return 0.05

def login(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('main:index'))
	else:
		return HttpResponseRedirect('/login/')
def register(request):
    template = loader.get_template('register.html')
    context={}
    if request.method=="POST":
        if request.POST['reg_student']:
            #create a user object here
            #store the user in the session and pass it to the next view
            return HttpResponseRedirect(reverse('main:reg_student'))
    return HttpResponse(template.render(context, request))

def reg_student(request):
    return render_to_response('reg_student.html',locals())
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
        return self.request.user.wallet.getHistory()
def addValue(request):
	request.user.wallet.addValue(100)
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
		return Tutor.objects.all().select_subclasses()



'''
class BioView(generic.DetailView):
	model = Tutor
	template_name = 'bio.html'
'''

#Olivia: added extimetable	4/11/17 22:41
def extimetable(request, TutorID):
    if request.method == "GET":

        tz = pytz.timezone('Asia/Hong_Kong')
        
        TargetTutor = subclassTutor(TutorID)
        TutorCourse = Course.objects.filter(tutorID = TutorID)


        
        Dates = []



        
        TodayDate = timezone.localtime(timezone.now()).date()
        
        StartDate = TodayDate - timedelta(days=TodayDate.weekday()) - timedelta(days=1)
        EndDate = StartDate + timedelta(days=13)
        #Dates.append(EndDate)
        
        for n in range(int((EndDate - StartDate).days)+1):
            TempDay = StartDate + timedelta(n)
            Dates.append(TempDay)
        
        now = timezone.localtime(timezone.now())
        sevenDaysLater = now + timedelta(days=7)
        
        ListOfSessions = []
        Hours = []
        found = 0
        appendonce = 0

        thisWeekDates = Dates[:7]
        nextWeekDates = Dates[-7:]



        #BookSessionOfTutor = Booking.objects.filter(tutor = TargetTutor.user)

        BookSessionOfTutor = Booking.objects.filter(Q(status="not yet begun") | Q(status="locked"), tutorID = TargetTutor.user, sessionDate__gte = TodayDate, sessionDate__lte = EndDate)
        SameDayBooking = Booking.objects.filter(Q(status="not yet begun") | Q(status="locked"), tutorID = TargetTutor.user, sessionDate__gte = TodayDate, sessionDate__lte = EndDate, studentID = request.user.myuser)

        SameDay=list(o.sessionDate for o in SameDayBooking)
        #TutorCourse = list(c.course for c in TutorCourseFullRecord)
        #CForm = CourseForm(instance=TargetTutor.user);

        #get respective session interval
        sessionInterval = TargetTutor.getSessionInterval()
        for eachdate in Dates:
            
            DateBookSessionOfTutor = Booking.objects.filter(tutorID = TargetTutor.user, sessionDate = eachdate)
            
            #24*60 is number of minutes in a day
            for smoketest in rrule.rrule(rrule.MINUTELY, interval=sessionInterval, dtstart=TodayDate, count=(24*60)/sessionInterval):
                eachhour = smoketest.strftime('%H:%M:%S')
                if not any(eachhour in s for s in Hours):
                    Hours.append(eachhour)
                
                #print smoketest
                found = 0
                
                
                tempbuttonid = eachdate.strftime('%Y%m%d') + smoketest.strftime('%H%M%S') + str(sessionInterval)

                #hereeeeeeee
                #if pytz.timezone("Asia/Hong_Kong").normalize(smoketest <= timezone.now():
                
                dtsmoketest = tz.localize(smoketest, is_dst=True)
                #print(dtsmoketest)
                #print timezone.now()
                if (eachdate<=timezone.localtime(timezone.now()).date()):
                    #OTB = Out of bound
                    tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)
                
                elif (eachdate>TodayDate + timedelta(days=7)):
                    tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)
                
                elif (dtsmoketest <= timezone.localtime(timezone.now()) and eachdate<=(timezone.localtime(timezone.now()).date() + timedelta(days=1))):
                    tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)

                else:

                    #check for booking history of that tutor
                    for x in DateBookSessionOfTutor:
                        
                        #string of Booked starttime of that tutor on that date
                        strx = x.startTime.strftime('%H:%M:%S')
                       
                        if strx == eachhour:
                            #print "yes"
                            found = 1
                            tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "Booked", eachhour, tempbuttonid)
                        
                    if found == 0:

                        
                        if eachdate in SameDay:                        
                            tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "SameDay", eachhour, tempbuttonid)
                        else:
                            tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "Free", eachhour, tempbuttonid)
                    
                ListOfSessions.append(tempsession)
        
        template = loader.get_template('extimetable.html')
        context = {'TargetTutor': TargetTutor, 'TodayDate': TodayDate, 'StartDate': StartDate, "EndDate": EndDate, "Dates": Dates, "thisWeekDates": thisWeekDates, "nextWeekDates":nextWeekDates, "Times": Hours, "ListOfSessions": ListOfSessions, 'TutorCourse' : TutorCourse}
        return HttpResponse(template.render(context, request))
    if request.method == "POST":
        Pressedbutton = request.POST.get('eachbutton', '')
        request.session['extimetableToConfirmBooking_token'] = Pressedbutton
        return HttpResponseRedirect('/search/%s/confirmbooking/' % TutorID)
	
def bio(request, TutorID):
    if request.method=="GET":

        TargetTutor = subclassTutor(TutorID)
        BookSessionOfTutor = Booking.objects.filter(tutorID = TargetTutor.user)
        TutorCourse = Course.objects.filter(tutorID = TutorID)
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
            DateBookSessionOfTutor = Booking.objects.filter(tutorID = TargetTutor.user, sessionDate = eachdate)
            
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
                    strx = x.startTime.strftime('%H:%M:%S')
                   
                    if strx == eachhour:
                        #print "yes"
                        found = 1
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(hours=1)), "Booked", eachhour, tempbuttonid)
                    
                if found == 0:
                    tempsession = Session(eachdate, eachhour, (smoketest+timedelta(hours=1)), "Free", eachhour, tempbuttonid)
                    
                ListOfSessions.append(tempsession)
    
    template = loader.get_template('bio2.html')
    #Sform = SessionForm()
    context = {'TargetTutor': TargetTutor, 'TodayDate': TodayDate, 'StartDate': StartDate, "EndDate": EndDate, "Dates": Dates, "Times": Hours, "ListOfSessions": ListOfSessions, 'TutorCourse': TutorCourse, }
    return HttpResponse(template.render(context, request))
    #reques
    #return PrivateTutorView.as_view()


def subclassTutor(TutorID):
    tempTutor = Tutor.objects.get_subclass(pk = TutorID)
    return type(tempTutor).objects.get(pk = TutorID)

class TutorView(generic.ListView):
    #model = Tutor
    template_name = 'bio2.html'
    context_object_name = 'TargetTutor'

    def get_queryset(self):
        TutorID = Tutor.objects.get_subclass(pk = self.kwargs['TutorID'])
        return type(TutorID).objects.get(pk = TutorID)


def confirmBooking(request, TutorID):
    
    if request.method=="GET":
        Pressedbutton = request.session['extimetableToConfirmBooking_token']
    
        t = Tutor.objects.get_subclass(pk=TutorID)
        
        #Pressedbutton = request.GET.get('eachbutton', '')
        buttonid = Pressedbutton

        sessionInterval = buttonid[-2:]
        
        date = datetime.strptime(buttonid[:8], '%Y%m%d').date()
        ChosenTime = datetime.strptime(buttonid[8:13], '%H%M%S').time()
        
        start=ChosenTime
        #assume 1hour first
        newhourdatetime = datetime.strptime(buttonid[:14], '%Y%m%d%H%M%S')+timedelta(minutes=int(sessionInterval))
        end = newhourdatetime.time()
        #assume bookings are all not yet begun

        #assume course is charged
        
        tutorUsername = t.user.user.username
        TutorCourse = Course.objects.filter(tutorID = TutorID)
        ######


        b = Booking(sessionDate=date, studentID=request.user.myuser, tutorID=t.user, startTime=start, endTime=end)
        #TFee = t.hourlyRate
        if hasattr(t, 'hourlyRate'):
            tutoringFee = t.hourlyRate
            commission = tutoringFee*getCommissionRate()
            totalPayable = tutoringFee + commission

            b.tutoringFee = tutoringFee
            b.commission = commission
            b.totalPayable = totalPayable

            ValidCouponObjList = Coupon.objects.getValidCoupon();
            ValidCouponObjList = Coupon.objects.getValidCoupon().values_list('id','couponCode')
            #ValidCouponList=list(cp.couponCode for cp in ValidCouponObjList)
            json_ValidCouponList = json.dumps(list(ValidCouponObjList))
            #json_ValidCouponList = serializers.serialize('json', (ValidCouponObjList))
            print json_ValidCouponList
            #json_ValidCouponList = json.dumps(ValidCouponList)

            '''
            for cp in ValidCouponObjList:
                print "yay"
                ValidCouponList.append = ["couponCode"]
                temp = cp.couponCode
                ValidCouponList.append(temp)
            json_ValidCouponList = json.dumps(ValidCouponList)
            '''
            print json_ValidCouponList
            context = {'b': b, 't':t, 'tutorUsername':tutorUsername, 'TutorCourse': TutorCourse, 'json_ValidCouponList': json_ValidCouponList,}
            template = loader.get_template('confirm_booking_withPayment.html')
            return HttpResponse(template.render(context, request))

        #do not save!
        #request.session['CancelBookData_Token'] = BookingData.Bookingid

        context = {'b': b, 't':t, 'tutorUsername':tutorUsername, 'TutorCourse': TutorCourse,}
        template = loader.get_template('confirm_booking.html')
        return HttpResponse(template.render(context, request))

    if request.method=="POST":
        b.status = "not yet begun"
        #put payment in
        b.save()
        print b.id
        bookingID = b.id        
        return HttpResponseRedirect('/booking/%s/' % bookingID)




    '''



    if request.method=="POST":
    	#buttonid = SessionForm(request.POST)
    	Pressedbutton = request.POST.get('eachbutton', '')
        CourseSelected = request.POST.get('CourseDrop', '')
        buttonid = Pressedbutton

        date = datetime.strptime(buttonid[:8], '%Y%m%d').date()
        ChosenTime = datetime.strptime(buttonid[-6:], '%H%M%S').time()
        print ChosenTime
        start=ChosenTime
        #assume 1hour first
        newhourdatetime = datetime.strptime(buttonid, '%Y%m%d%H%M%S')+timedelta(hours=1)
        end = newhourdatetime.time()
        #assume bookings are all not yet begun
        b = Booking(session_date=date, student=request.user.myuser,tutor=t.user, start_time=start, end_time=end, tutoring_fee=t.hourly_rate, commission=t.hourly_rate*0.05, total_payable=t.hourly_rate+t.hourly_rate*0.05, status="not yet begun")
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
    '''
    


def confirmBookingold(request, TutorID):
    t = Tutor.objects.get(pk=TutorID)
    if request.method=="POST":
        #buttonid = SessionForm(request.POST)
        Pressedbutton = request.POST.get('eachbutton', '')
        CourseSelected = request.POST.get('CourseDrop', '')
        buttonid = Pressedbutton

        date = datetime.strptime(buttonid[:8], '%Y%m%d').date()
        ChosenTime = datetime.strptime(buttonid[-6:], '%H%M%S').time()
        start=ChosenTime
        #assume 1hour first
        newhourdatetime = datetime.strptime(buttonid, '%Y%m%d%H%M%S')+timedelta(hours=1)
        end = newhourdatetime.time()
        #assume bookings are all not yet begun
        print CourseSelected

        CourseObj = Course.objects.get(tutorID = t, course__CourseCode = CourseSelected)
        SubjectName = CourseCatalogue.objects.get(CourseCode = CourseSelected).getCourseName()


        #assume course is charged
        TFee = CourseObj.hourly_rate
        #GetAllValidCoupon
        

        print ValidCouponList




        b = Booking(session_date=date, student=request.user.myuser,tutor=t.user, start_time=start, end_time=end, course=CourseObj.course, tutoring_fee=TFee, commission=TFee*0.05, total_payable=TFee*1.05)
        #do not save!
        context = {'b': b, 't':t, 'SubjectName' : SubjectName, 'ValidCouponList' : ValidCouponList}
        template = loader.get_template('confirm_booking.html')
        return HttpResponse(template.render(context, request))

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


def BookingDetails(request, pk):
    
    if request.method == 'POST':
        if 'cancelsession' in request.POST:
            #cancel
            BookingData = Booking.objects.get(pk = pk)
            request.session['CancelBookData_Token'] = BookingData.Bookingid
            ############################################
            return HttpResponseRedirect('/tutor/BookingDetails_stu/%s/ConfirmCancellation/' % BookingID)
         
    print "BookingDetails"
    print pk
    booking = Booking.objects.get(pk = pk)
    
    template = loader.get_template('booking_details.html')
    context = {'booking': booking, }
    return HttpResponse(template.render(context, request))


class BookingDetailView(generic.DetailView):


    template_name = 'booking_details.html'
    model = Booking
    def get_queryset(self):
        #print bookingID
        BookingData = Booking.objects.get(pk = self.kwargs['bookingID'])
        template = loader.get_template('booking_details.html')
        context = {'BookingData': BookingData, }
        return HttpResponse(template.render(context, request))
        


