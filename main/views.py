# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import json
from django.contrib.auth.models import User
from datetime import datetime, date, time, timedelta
from django.shortcuts import render, render_to_response, redirect
from django.views import generic
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import myUser, Tutor, PrivateTutor, ContractTutor, Booking, Transaction, Wallet, Session, Course, Coupon, Student, Blackout, Payment,CourseCatalogue, Review
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
from .forms import SessionForm, StudentRegisterForm, TutorRegisterForm, BothRegisterForm
from django.contrib.auth import views
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
#Olivia: 7/11/17 14:50
from django.db.models import Q
import pytz
from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from django.db.models import Avg

# Create your views here.
class passwordResetView(views.PasswordResetView):
    template_name="forgetPassword.html"

class passwordResetDoneView(views.PasswordResetDoneView):
    template_name="passwordResetSuccess.html"

class passwordResetConfirmView(views.PasswordResetConfirmView):
    template_name="passResetForm.html"
    success_url="/reset/done/"

class passwordResetCompleteView(views.PasswordResetCompleteView):
    template_name="passwordResetComplete.html"

class passwordChangeView(views.PasswordChangeView):
    template_name="passwordChange.html"
class passwordChangeDoneView(views.PasswordChangeDoneView):
    template_name="passwordChangeDone.html"


def getCommissionRate():
    return 0.05

def checkEnough(request):
    if request.method == 'GET':
        amount = request.GET.get('amount',"")
        exists = request.user.wallet.enough(amount)
        return JsonResponse({'exists': exists})
    
def checkCouponCode(request):
    if request.method == 'GET':
        inputcode = request.GET.get('InCoupon',"")

        exists = Coupon.objects.isCouponValid(inputcode).exists()
        #ValidCouponList=list(cp.couponCode for cp in ValidCouponObjList)
        return JsonResponse({'exists': exists})

def checkUsername(request):
    if request.method == 'GET':
        username = request.GET.get('username',"")
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})

def checkEmail(request):
    if request.method == 'GET':
        if request.GET.get('username') and request.GET.get('email'):
            if User.objects.filter(username=request.GET.get('username')).exists():                
                user = User.objects.get(username=request.GET.get('username'))
                if user.email == request.GET.get('email'):
                    return JsonResponse({'valid': True})
            else:
                return JsonResponse({'valid': False})
        email = request.GET.get('email',"")
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'exists': exists})

def getCourseSet(request):
    if request.method == 'GET':
        course_set = request.user.myuser.tutor.course_set.all()
        course_list = []
        for course in course_set:
            course_list.append(course.courseCode.courseCode)
        return JsonResponse({'course_list': course_list})

def getCommissionRate():
    return 0.05

def login(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('main:index'))
	else:
		return HttpResponseRedirect('/login/')

@staff_member_required
def manage_sessions(request):
    return render(request,'manageSessions.html')

def bio_review(TutorID):
    #print request.user.myuser.id
    TargetTutor = Tutor.objects.get(id=TutorID)
    review_list = TargetTutor.review_set.all().order_by('-timestamp')

    #calculate average
    reviewAvg = review_list.aggregate(Avg('rate'))
    return review_list, reviewAvg
    #return render(request,'comment.html', {'review_list': review_list})

def end_all_sessions(request):
    booking_list = Booking.objects.filter(Q(sessionDate__lte=timezone.localtime(timezone.now()).date()), Q(endTime__lte = timezone.localtime(timezone.now()).time()), ~Q(status="ended"))
    for booking in booking_list:
        booking.end()
    return redirect('main:manage_sessions')

def profile(request):
    course_catalogue = CourseCatalogue.objects.all().distinct()
    return render(request,'userProfile.html', {'course_catalogue': course_catalogue,})

def review(request, bookingID):
    if hasattr(request.user,"myuser"):
        booking = Booking.objects.get(id=bookingID)
        if request.user.myuser == booking.studentID:
            if request.method == 'POST':
                rating = request.POST.get("star_rating")
                if request.POST.get("comment"):
                    comment = request.POST.get("comment")
                booking.isReiew = True
                booking.save()
                review = Review(tutorID=booking.tutorID.tutor,studentID=booking.studentID.student, bookingID=booking, rate=rating, description=comment)
                review.save()
            return render(request,'review.html')
    return redirect('main:index')
def forget(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        user = User.objects.get(username=username)
        send_mail(
            'Retrieve Password',
            'Hello '+ username + ". Here is your password: "+user.password,
            'myTutor@solveware.com',
            [email],
            fail_silently=False,
        )
    return render(request,'forgetPassword.html')

def updateprofile(request):
    if request.method=="POST":
        tutor = request.user.myuser.tutor
        tutor.description = request.POST.get("description","")
        if request.POST.get("isactivated") == "on":
            tutor.isactivated = True
        else:
            tutor.isactivated = False
        #print request.POST.get("type","")
        if request.POST.get("type","")=="Private Tutor":
            print request.POST.get("hourly_rate","")
            tutor.privatetutor.hourlyRate = request.POST.get("hourly_rate","")
            tutor.privatetutor.save()
        tutor.save()
        course = request.POST.getlist("courseCode","")
        hiddencourse = request.POST.getlist("hiddenCourseCode","")
        for courseCode in course:
            courseObj = CourseCatalogue.objects.get(courseCode=courseCode)
            if not request.user.myuser.tutor.course_set.all().filter(courseCode=courseObj).exists():
                tag = Course(tutorID=request.user.myuser.tutor, courseCode=courseObj)
                tag.save()
        for hiddencourseCode in hiddencourse:
            courseObject = CourseCatalogue.objects.filter(courseCode=hiddencourseCode)
            teachIn = Course.objects.filter(courseCode=courseObject)
            for x in teachIn:
                teachIn.delete()
    return redirect('main:profile')

def register(request):
    template = loader.get_template('register.html')
    context={}
    if request.method=="POST":
        if 'reg_student' in request.POST:
            return HttpResponseRedirect(reverse('main:reg_student'))
        elif 'reg_tutor' in request.POST:
            return HttpResponseRedirect(reverse('main:reg_tutor'))
        else:
            return HttpResponseRedirect(reverse('main:reg_both'))

    return HttpResponse(template.render(context, request))

def reg_student(request):
    if request.method=="POST":
        form = StudentRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            usr = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password1'])
            usr.first_name = form.cleaned_data['firstName']
            usr.last_name = form.cleaned_data['lastName']
            if form.cleaned_data['image'] == None:
                print "here"
                myUsr = myUser(user=usr, tel=form.cleaned_data['tel'])
            else:
                myUsr = myUser(user=usr, tel=form.cleaned_data['tel'], profilePicture=form.cleaned_data['image'])
            school = request.POST['school']
            usr.save()
            wallet = Wallet(user=usr,balance=0)
            wallet.save()
            myUsr.save()
            stud = Student.objects.create_student(myUsr, school)
            stud.save()
            return redirect('main:reg_success', type="student")
    return render(request,'reg_student.html')

def reg_tutor(request):
    if request.method=="POST":
        form = TutorRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            usr = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password1'])
            usr.first_name = form.cleaned_data['firstName']
            usr.last_name = form.cleaned_data['lastName']
            if form.cleaned_data['image'] == None:
                print "here"
                myUsr = myUser(user=usr, tel=form.cleaned_data['tel'])
            else:
                myUsr = myUser(user=usr, tel=form.cleaned_data['tel'], profilePicture=form.cleaned_data['image'])
            school = request.POST['school']
            wallet = Wallet(user=usr,balance=0)
            usr.save()
            wallet.save()
            myUsr.save()
            if form.cleaned_data['type']=="private":
                tutor = PrivateTutor.objectManager.create_tutor(myUsr, school,form.cleaned_data['description'], form.cleaned_data['type'], form.cleaned_data['hourly_rate'])
            else:
                tutor = ContractTutor.objectManager.create_tutor(myUsr, school,form.cleaned_data['description'], form.cleaned_data['type'], form.cleaned_data['hourly_rate'])          
            tutor.save()
            return redirect('main:reg_success', type= form.cleaned_data['type'] + "tutor")
    return render(request,'reg_tutor.html')

def reg_both(request):
    if request.method=="POST":
        form = BothRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            usr = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password1'])
            usr.first_name = form.cleaned_data['firstName']
            usr.last_name = form.cleaned_data['lastName']
            if form.cleaned_data['image'] == None:
                print "here"
                myUsr = myUser(user=usr, tel=form.cleaned_data['tel'])
            else:
                myUsr = myUser(user=usr, tel=form.cleaned_data['tel'], profilePicture=form.cleaned_data['image'])
            school1 = form.cleaned_data['school1']
            school2 = form.cleaned_data['school2']
            wallet = Wallet(user=usr,balance=0)
            usr.save()
            wallet.save()
            myUsr.save()
            stud = Student.objects.create_student(myUsr, school1)
            stud.save()
            if form.cleaned_data['type']=="private":
                tutor = PrivateTutor.objectManager.create_tutor(myUsr, school2,form.cleaned_data['description'], form.cleaned_data['type'], form.cleaned_data['hourly_rate'])
            else:
                tutor = ContractTutor.objectManager.create_tutor(myUsr, school2,form.cleaned_data['description'], form.cleaned_data['type'], form.cleaned_data['hourly_rate'])          
            tutor.save()
            return redirect('main:reg_success', type= "both")
    return render(request,'reg_both.html')

def reg_success(request, type):
    return render(request,'registerSuccess.html', {'type': type,})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def index(request):
    return render_to_response('index.html',locals())

def bookFail(request):
    return render(request,'bookFail.html')

class WalletView(generic.ListView):
    template_name = 'wallet.html'
    context_object_name = 'transaction_history'
    def get_queryset(self):
        """Return the last five published questions."""
        return self.request.user.wallet.getHistory()


def addValue(request):
    request.user.wallet.add(100)
    value=100
    t = Transaction(senderID=request.user, receiverID=request.user, transactionAmount=value, action="Add Value", status=Transaction.TD)
    print "!23"
    t.save()
    return HttpResponseRedirect(reverse('main:wallet'))

def withDrawValue(request):
    request.user.wallet.minus(100)
    value=100
    t = Transaction(senderID=request.user, receiverID=request.user, transactionAmount=value, action=Transaction.WL, status=Transaction.TD)
    t.save()
    return HttpResponseRedirect(reverse('main:wallet'))

@staff_member_required    
def addValue_admin(request):
    value=100
    admin = User.objects.get(username="mytutors")
    admin.wallet.add(100)
    t = Transaction(senderID=request.user, receiverID=admin, transactionAmount=value, action="Add Value", status=Transaction.TD)
    t.save()
    return HttpResponseRedirect(reverse('main:wallet'))

@staff_member_required    
def withDrawValue(request):
    value=100
    admin = User.objects.get(username="mytutors")
    admin.wallet.minus(100)
    t = Transaction(senderID=admin, receiverID=admin, transactionAmount=value, action=Transaction.WL, status=Transaction.TD)
    t.save()
    return HttpResponseRedirect(reverse('main:wallet'))

class BookingHistoryView(generic.ListView):
    template_name = 'booking_history.html'
    context_object_name = 'booking_history'
    def get_queryset(self):
        """Return the last five published questions."""
        return Booking.objects.filter(Q(studentID=self.request.user.myuser) | Q(tutorID=self.request.user.myuser) ).order_by('-timestamp')[:7]

class SearchResultView(generic.ListView):
	template_name = 'searchResults.html'
	context_object_name = 'ListOfTutor'
	def get_queryset(self):
		return Tutor.objects.all().select_subclasses()



def extimetable(request, TutorID):
    if request.method == "GET":
        context = customTimetable(TutorID, request.user.myuser)        
        template = loader.get_template('extimetable.html')

        #context = {'TargetTutor': TargetTutor, 'TodayDate': TodayDate, 'StartDate': StartDate, "EndDate": EndDate, "Dates": Dates, "thisWeekDates": thisWeekDates, "nextWeekDates":nextWeekDates, "Times": Hours, "ListOfSessions": ListOfSessions, 'TutorCourse' : TutorCourse}
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        Pressedbutton = request.POST.get('eachbutton', '')
        request.session['extimetableToConfirmBooking_token'] = Pressedbutton
        return HttpResponseRedirect('/search/%s/confirmbooking/' % TutorID)



def customIntimetable(request, type):

    tz = pytz.timezone('Asia/Hong_Kong')
    now = timezone.localtime(timezone.now())
    TodayDate = timezone.localtime(timezone.now()).date() 
    Dates = []
    Dates = getTimetableDateRange()

    thisWeekDates = Dates[:7]
    nextWeekDates = Dates[-7:]


    ListOfSessions = []
    Hours = []
    booked_found = 0
    appendonce = 0

    sessionInterval = 30
    for eachdate in Dates:
        
        #get the bookings of the tutor on a particular day
        ownBooking = Booking.objects.getRelatedBooking(request.user.myuser, eachdate)

        #get the blackouts of the tutor on a particular day
        #assume tutor first
        BlackOutTutor = ""
        BlackOut_eachdate_time = []
        if (type == "Tutor"):
            TargetTutor = Tutor.objects.get(user = request.user.myuser)
            BlackOutTutor = Blackout.objects.getBlackOutTutorDate(TargetTutor, eachdate)
            BlackOut_eachdate_time=list(bo.startTime for bo in BlackOutTutor)
        
        #24*60 is number of minutes in a day
        for smoketest in rrule.rrule(rrule.MINUTELY, interval=sessionInterval, dtstart=TodayDate, count=(24*60)/sessionInterval):
            eachhour = smoketest.strftime('%H:%M:%S')
            if not any(eachhour in s for s in Hours):
                Hours.append(eachhour)
            
            
            booked_found = 0          
            
            tempbuttonid = eachdate.strftime('%Y%m%d') + smoketest.strftime('%H%M%S') + str(sessionInterval)

            dtsmoketest = tz.localize(smoketest, is_dst=True)
            #print dtsmoketest
            
            #define those dates that are out of booking range
            if (eachdate<=TodayDate):
                
                tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)
            
            elif (eachdate>TodayDate + timedelta(days=7)):
                tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)
            
            elif (dtsmoketest <= now and eachdate<=(TodayDate + timedelta(days=1))):
                tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)

            else:

                #check for booking history of that tutor
                for x in ownBooking:
                    
                    #string of Booked starttime of that tutor on that date
                    strx = x.startTime.strftime('%H:%M:%S')
                    stre = x.endTime.strftime('%H:%M:%S')
                   
                    if (eachhour >= strx and eachhour < stre):
                        
                        booked_found = 1
                        tempbuttonid = x.id
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "Booked", eachhour, tempbuttonid)
                #if the session is not booked
                if booked_found == 0:

                    #if student has booked the tutor on that day
                    if dtsmoketest.time() in BlackOut_eachdate_time:
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "BlackOut", eachhour, tempbuttonid)
                    #session is free
                    else:
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "Free", eachhour, tempbuttonid)
                
            ListOfSessions.append(tempsession)

    context = {"Dates": Dates, "thisWeekDates": thisWeekDates, "nextWeekDates":nextWeekDates, "Times": Hours, "ListOfSessions": ListOfSessions,}
    return context

def intimetable(request):
    if (hasattr(request.user.myuser, "tutor")):
        return redirect('main:intimetable_tutor')
    elif (hasattr(request.user.myuser, "student")):
        return redirect('main:intimetable_student')

    
    else:
        print "None!!!"

def intimetable_student(request):
    
    if request.method=="POST":
        if (request.POST.get('eachbutton', False) != False):
            Pressedbutton = request.POST.get('eachbutton', '')
            return HttpResponseRedirect('/booking/%s/' % Pressedbutton)
        

    context = customIntimetable(request, "Student")

    #context = {"Dates": Dates, "thisWeekDates": thisWeekDates, "nextWeekDates":nextWeekDates, "Times": Hours, "ListOfSessions": ListOfSessions,}
    template = loader.get_template('intimetable_student.html')
    return HttpResponse(template.render(context, request))

def intimetable_tutor(request):
    
    if request.method=="POST":
        if (request.POST.get('eachbutton', False) != False):
            Pressedbutton = request.POST.get('eachbutton', '')
            return HttpResponseRedirect('/booking/%s/' % Pressedbutton)
        else:
            print "intimetable POST"
            #add new blackout
            addList = request.POST.get("HiddenNew", False)
            

            for i in range(0, len(addList), 16):
                eachbutton = addList[i:i + 16] 

                buttondata = translateButtonid(eachbutton)
                print buttondata

                TargetTutor = Tutor.objects.get(user = request.user.myuser)
                bo = Blackout.objects.create_blackout(TargetTutor, buttondata['sessionDate'], buttondata['startTime'], buttondata['endTime'])
                print bo
                bo.save()
                #add record to blackout


            
            removeList = request.POST.get('HiddenRemove', False)
            for i in range(0, len(removeList), 16):
                eachbutton = removeList[i:i + 16]

                buttondata = translateButtonid(eachbutton)
                print buttondata
                Blackout.objects.getBlackOutTutorDateTime(request.user.myuser.tutor, buttondata['sessionDate'], buttondata['startTime']).delete()
                


    context = customIntimetable(request, "Tutor")

    #context = {"Dates": Dates, "thisWeekDates": thisWeekDates, "nextWeekDates":nextWeekDates, "Times": Hours, "ListOfSessions": ListOfSessions,}
    template = loader.get_template('intimetable_tutor.html')
    return HttpResponse(template.render(context, request))

def bio(request, TutorID):
    if request.method == "GET":

        context = customTimetable(TutorID, request.user.myuser)        
        template = loader.get_template('bio2.html')
        review_list, reviewAvg = bio_review(TutorID)
        context['review_list'] = review_list
        context['reviewAvg'] = reviewAvg
        #context = {'TargetTutor': TargetTutor, 'TodayDate': TodayDate, 'StartDate': StartDate, "EndDate": EndDate, "Dates": Dates, "thisWeekDates": thisWeekDates, "nextWeekDates":nextWeekDates, "Times": Hours, "ListOfSessions": ListOfSessions, 'TutorCourse' : TutorCourse}
        return HttpResponse(template.render(context, request))

def getTimetableDateRange():
    Dates = []        
    TodayDate = timezone.localtime(timezone.now()).date()        
    StartDate = TodayDate - timedelta(days=TodayDate.weekday()) - timedelta(days=1)
    EndDate = StartDate + timedelta(days=13)
    for n in range(int((EndDate - StartDate).days)+1):
        TempDay = StartDate + timedelta(n)
        Dates.append(TempDay)
    return Dates


def customTimetable(TutorID, own):
    
    tz = pytz.timezone('Asia/Hong_Kong')        
    #get subclass of tutor
    TargetTutor = subclassTutor(TutorID)
    #get the course taught by tutor
    TutorCourse = Course.objects.getCourse(TargetTutor)

    #calculation of date range to display    
    
    now = timezone.localtime(timezone.now())
    TodayDate = timezone.localtime(timezone.now()).date() 
    Dates = []
    Dates = getTimetableDateRange()
    
    
    ListOfSessions = []
    Hours = []
    booked_found = 0
    appendonce = 0

    thisWeekDates = Dates[:7]
    nextWeekDates = Dates[-7:]

    #get the booking of the student and tutor
    #SameDayBooking = Booking.objects.filter(Q(status="not yet begun") | Q(status="locked"), tutorID = TargetTutor.user, sessionDate__gte = TodayDate, sessionDate__lte = EndDate, studentID = request.user.myuser)
    SameDayBooking = TargetTutor.getSameStudentBooking(TodayDate, TodayDate+timedelta(days=8), own)
    SameDay=list(o.sessionDate for o in SameDayBooking)
    
    
    #get the session interval of the tuto  xr type
    sessionInterval = TargetTutor.getSessionInterval()
    for eachdate in Dates:
        
        #get the bookings of the tutor on a particular day
        
        if (hasattr(own, "tutor") and hasattr(own, "student")):
            print "student and tutor"
            DateBookSessionOfTutor = own.tutor.getTutorBooking(eachdate) | TargetTutor.getTutorBooking(eachdate)
        else:
            DateBookSessionOfTutor = TargetTutor.getTutorBooking(eachdate)

        #get the blackouts of the tutor on a particular day
        BlackOutTutor = Blackout.objects.getBlackOutTutorDate(TutorID, eachdate)
        BlackOut_eachdate_time=list(bo.startTime for bo in BlackOutTutor)
        
        #24*60 is number of minutes in a day
        for smoketest in rrule.rrule(rrule.MINUTELY, interval=sessionInterval, dtstart=TodayDate, count=(24*60)/sessionInterval):
            eachhour = smoketest.strftime('%H:%M:%S')
            if not any(eachhour in s for s in Hours):
                Hours.append(eachhour)
            
            
            booked_found = 0
            
            
            tempbuttonid = eachdate.strftime('%Y%m%d') + smoketest.strftime('%H%M%S') + str(sessionInterval)

            dtsmoketest = tz.localize(smoketest, is_dst=True)
            #print dtsmoketest
            
            #define those dates that are out of booking range
            if (eachdate<=TodayDate):
                
                tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)
            
            elif (eachdate>TodayDate + timedelta(days=7)):
                tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)
            
            elif (dtsmoketest <= now and eachdate<=(TodayDate + timedelta(days=1))):
                tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "OOB", eachhour, tempbuttonid)

            else:

                #check for booking history of that tutor
                for x in DateBookSessionOfTutor:
                    
                    #string of Booked starttime of that tutor on that date
                    strx = x.startTime.strftime('%H:%M:%S')
                   
                    if strx == eachhour:
                        
                        booked_found = 1
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "Booked", eachhour, tempbuttonid)
                #if the session is not booked
                if booked_found == 0:

                    #if student has booked the tutor on that day
                    if eachdate in SameDay:                        
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "SameDay", eachhour, tempbuttonid)
                    #if the session is blacked out by the tutor
                    elif dtsmoketest.time() in BlackOut_eachdate_time:
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "BlackOut", eachhour, tempbuttonid)
                    #session is free
                    else:
                        tempsession = Session(eachdate, eachhour, (smoketest+timedelta(minutes=sessionInterval)), "Free", eachhour, tempbuttonid)
                
            ListOfSessions.append(tempsession)
        
    
    context = {'TargetTutor': TargetTutor, 'TodayDate': TodayDate, "Dates": Dates, "thisWeekDates": thisWeekDates, "nextWeekDates":nextWeekDates, "Times": Hours, "ListOfSessions": ListOfSessions, 'TutorCourse' : TutorCourse}
    return context   


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

def translateButtonid(buttonid):
    sessionInterval = buttonid[-2:]
    date = datetime.strptime(buttonid[:8], '%Y%m%d').date()
    ChosenTime = datetime.strptime(buttonid[8:13], '%H%M%S').time()
    newhourdatetime = datetime.strptime(buttonid[:14], '%Y%m%d%H%M%S')+timedelta(minutes=int(sessionInterval))
    end = newhourdatetime.time()

    buttondata = {'sessionDate': date, 'startTime': ChosenTime, 'endTime': end}
    return buttondata




def confirmBooking(request, TutorID):
    t = Tutor.objects.get_subclass(pk=TutorID)
    
    Pressedbutton = request.session['extimetableToConfirmBooking_token']
    
    buttondata = translateButtonid(Pressedbutton)
    #assume bookings are all not yet begun
    
    tutorUsername = t.user.user.username
    TutorCourse = Course.objects.filter(tutorID = TutorID)
    ######


    b = Booking(sessionDate=buttondata['sessionDate'], studentID=request.user.myuser, tutorID=t.user, startTime=buttondata['startTime'], endTime=buttondata['endTime'], tutoringFee=0, commission=0, totalPayable=0)
    if request.method=="GET":
        #TFee = t.hourlyRate
        if hasattr(t, 'hourlyRate'):
            tutoringFee = t.hourlyRate
            commission = tutoringFee*getCommissionRate()
            totalPayable = tutoringFee + commission

            b.tutoringFee = tutoringFee
            b.commission = commission
            b.totalPayable = totalPayable

            
            
            context = {'b': b, 't':t, 'tutorUsername':tutorUsername, 'TutorCourse': TutorCourse, }
            template = loader.get_template('confirm_booking_withPayment.html')
            return HttpResponse(template.render(context, request))

        #do not save!
        #request.session['CancelBookData_Token'] = BookingData.Bookingid

        context = {'b': b, 't':t, 'tutorUsername':tutorUsername, 'TutorCourse': TutorCourse,}
        template = loader.get_template('confirm_booking.html')
        return HttpResponse(template.render(context, request))

    if request.method=="POST":
        
        if hasattr(t, 'hourlyRate'):
            CouponUsed = request.POST.get('CouponUsed', '')

            tutoringFee = t.hourlyRate

            if (CouponUsed == "Yes"):
                commission = 0;
                
            else:
                commission = tutoringFee*getCommissionRate()
                

            totalPayable = tutoringFee + commission

            b.tutoringFee = tutoringFee
            b.commission = commission
            b.totalPayable = totalPayable
            
            #make payment
            bookingResults = b.createPayment()
            if (bookingResults == False):
                #failed
                print ("bookingflag == False")
                return redirect('main:bookFail')
                



        

        b.status = "not yet begun"
        b.timestamp = timezone.localtime(timezone.now())

        #put payment in
        b.save()
        bookingID = b.id
        if hasattr(t, 'hourlyRate'):

            print b.id
            bookingResults.bookingID = b
            bookingResults.createTransaction()
        b.book()
        return HttpResponseRedirect('/booking/%s/' % bookingID)




class CancelView(generic.DetailView):
	model = Booking
	template_name = 'cancel.html'


def ConfirmCancel(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = "Cancelled"
    booking.save()
    if (booking.totalPayable != 0):
        #get transaction
        t = Transaction.objects.get(bookingID = booking)
        t.cancel()

    #booking cancel
    booking.cancel()

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
    booking = Booking.objects.get(pk = pk)
    if (request.user.myuser == booking.studentID):
        interfaceType = "Student"
    else:
        interfaceType = "Tutor"
    
    template = loader.get_template('booking_details.html')
    context = {'booking': booking, 'interfaceType': interfaceType}
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
        


