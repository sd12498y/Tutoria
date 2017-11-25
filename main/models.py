# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models import Q
from django.core.mail import send_mail
from notifications.signals import notify

from django.utils import timezone
from django.utils.timezone import localtime
from model_utils.managers import InheritanceManager
from django.core import serializers
from django.http import JsonResponse
import time
from datetime import datetime, date, time, timedelta
from django.core.mail import EmailMultiAlternatives

import pytz


class myUserManager(models.Manager):
	def create_myUser(self, user, tel, *profilePicture):
		myUser = self.create(user=user, tel=tel, profilePicture=profilePicture)
		return myUser

class myUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	tel = models.CharField(max_length=8)
	profilePicture = models.FileField(upload_to='static/img/propic/', default='static/img/propic/blank.png')

	objects = myUserManager()

	def __str__(self):
		return '%s' % (self.user.username)
	

class myTutor(models.Model):
	staff = models.OneToOneField(User, related_name='staff', on_delete=models.CASCADE)
	admin = models.ForeignKey(User, related_name='admin', on_delete=models.CASCADE)

	def __str__(self):
		return '%s' % (self.staff.username)

class StudentManager(models.Manager):
	def create_student(self, user, university):
		student = self.create(user=user, university=university)
		return student

class Student (models.Model):
	user = models.OneToOneField(myUser, on_delete=models.CASCADE)
	university = models.CharField(max_length=50)
	objects =StudentManager()

	def __str__(self):
		return '%s' % (self.user.user.username)


class TutorManager(models.Manager):
	def create_tutor(self, user, university, description, type, hourlyRate):
		if type=="private":
			return self.create(user=user, university=university, description=description, hourlyRate=hourlyRate)
		else:
			return self.create(user=user, university=university, description=description)
	def getRelatedBooking(self, sessionDate):
		relatedBooking = Booking.objects.filter(Q(status="not yet begun") | Q(status="locked")| Q(status="completed"), tutorID = self.user, sessionDate = sessionDate)
		return relatedBooking


class Tutor(models.Model):
	
	user = models.OneToOneField(myUser, on_delete=models.CASCADE)
	university = models.CharField(max_length=50)
	description = models.TextField()
	isactivated = models.BooleanField(default=True)
	
	objectManager = TutorManager()
	objects = InheritanceManager()

	def __str__(self):
		return '%s' % (self.user.user.username)
	def getSameStudentBooking(self, startDate, endDate, studentID):
		return Booking.objects.filter(Q(status="not yet begun") | Q(status="locked"), tutorID = self.user, sessionDate__gte = startDate, sessionDate__lte = endDate, studentID = studentID)
	def getTutorBooking(self, sessionDate):
		return Booking.objects.filter(Q(status="not yet begun") | Q(status="locked"), tutorID = self.user, sessionDate = sessionDate)



class PrivateTutor(Tutor):
	hourlyRate = models.FloatField(default=0, null=True)
	def extimetable_get_fields(self):
		list = []

		temp = ("Tutor Name", self.user.user.first_name+" " +self.user.user.last_name)
		list.append(temp)
		temp = ("University", self.university)
		list.append(temp)	
		temp = ("Hourly Rate", "$" + str(self.hourlyRate))
		list.append(temp)
		return list
	def getSessionInterval(self):
		return 60
	def tutor_upper_get_fields(self):
		list = []

		temp = ("Tutor Name", self.user.user.first_name+" " +self.user.user.last_name)
		list.append(temp)
		temp = ("Username", self.user.user.username)
		list.append(temp)
		temp = ("Tutor Type", "Private Tutor")
		list.append(temp)
		for field in PrivateTutor._meta.fields:
			if (field.name == "hourlyRate"):
				temp = ("Hourly Rate", "$"+field.value_to_string(self))
				list.append(temp)
			elif ((field.name == "user") or (field.name == "tutor_ptr") or (field.name == "user") or (field.name == "id")):
				temp = ("", "")
				#list.append(temp)
			elif (field.name == "university"):
				temp = ("University", field.value_to_string(self))
				list.append(temp)
			elif (field.name == "description"):
				temp = ("Description", field.value_to_string(self))
				list.append(temp)
			else:
				temp = (field.name, field.value_to_string(self))
				list.append(temp)
		
		return list

		#return [(field.name, field.value_to_string(self)) for field in PrivateTutor._meta.fields]
class ContractTutor(Tutor):
	ContractID = models.CharField(max_length=30, default='')
	def extimetable_get_fields(self):
		list = []

		temp = ("Tutor Name", self.user.user.first_name+" " +self.user.user.last_name)
		list.append(temp)
		temp = ("University", self.university)
		list.append(temp)
		return list
	def getSessionInterval(self):
		return 30
	def tutor_upper_get_fields(self):
		list = []

		temp = ("Tutor Name", self.user.user.first_name+" " +self.user.user.last_name)
		list.append(temp)
		temp = ("Username", self.user.user.username)
		list.append(temp)
		temp = ("Tutor Type", "Contracted Tutor")
		list.append(temp)
		for field in ContractTutor._meta.fields:
			if (field.name == "ContractID") or (field.name == "tutor_ptr") or (field.name == "user") or (field.name == "id"):
				temp = ("","")
			elif (field.name == "university"):
				temp = ("University", field.value_to_string(self))
				list.append(temp)
			elif (field.name == "description"):
				temp = ("Description", field.value_to_string(self))
				list.append(temp)
			else:
				temp = (field.name, field.value_to_string(self))
				list.append(temp)
		return list


class Session (models.Model):
	#Sessionid = models.CharField(max_length=30, default='DEFAULTUSERID')
	SessionDate = models.DateField(auto_now_add=False, null=True, blank=True)
	StartTime = models.TimeField(auto_now_add=False, null=True, blank=True)
	EndTime = models.TimeField(auto_now_add=False, null=True, blank=True)
	Status = models.CharField(max_length=30, default='DEFAULTSTATUS')
	Buttonid = models.CharField(max_length=14, default='00000000000000')
	def __init__(self, SessionDate=None, StartTime=None, EndTime=None, Status=None, StrStartTime=None, Buttonid=None):
		self.SessionDate = SessionDate
		self.StartTime = StartTime
		self.EndTime = EndTime
		self.Status = Status
		self.StrStartTime = StrStartTime
		self.Buttonid = Buttonid

class WalletManager(models.Manager):
	def pay(self, userID, value):
		print ("pay()")
		target = Wallet.objects.get(user = userID)
		if (target.enoughMoney(value) == True):
			print ("enoughMoney() returns true")
			company = User.objects.get(username = "mytutors")
			target.balance -= value
			target.save()
			notify.send(company, recipient=target.user, verb='$'+str(value)+' has been withdrawn from your wallet')
			send_mail(
			    '$'+str(value)+' has been withdrawn from your wallet',
			    'Here is the message.',
			    [company.email],
			    [target.user.email],
			    fail_silently=False,
			)
			return True
		else:
			print ("enoughMoney() returns false")
			return False
	def receive(self, userID, value):
		target = Wallet.objects.get(user = userID)		
		company = User.objects.get(username = "mytutors")
		target.balance += value
		target.save()
		notify.send(company, recipient=target.user, verb='$'+str(value)+' has been added from your wallet')
		send_mail(
		    '$'+str(value)+' has been added from your wallet',
		    'Here is the message.',
		    [company.email],
		    [target.user.email],
		    fail_silently=False,
		)


class Wallet(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	balance = models.FloatField()
	objects = WalletManager()
	def enoughMoney(self, value):
		print ("enoughMoney()")
		if (self.balance < value):
			return False
		else:
			return True
			
	def refund(self,value,tutor):
		self.balance += value
		self.save()
		#t = Transaction(payer=mytutors , receiver=self.user, amount=value, action="Refund")
		#t.save()
		notify.send(self.user, recipient=tutor.user, verb='Booking has been cancelled.' )
		notify.send(self.user, recipient=self.user, verb='Booking has sucessfully been cancelled.' )
		send_mail(
	    'Booking cancellation',
	    'Booking has been cancelled.',
	    'system@solveware.com',
	    ['test@solveware.com'],
	    fail_silently=False,
		)
		return

	def add(self,value):
		self.balance += value
		self.save()
		notify.send(self.user, recipient=self.user, verb='$'+str(value)+' has been added to your wallet')
		send_mail(
		    '$'+str(value)+' has been added to your wallet',
		    'Hello ' + self.user.username + '. This is to notify you that $' + str(value) +' has recently been added to your wallet',
		    'system@solveware.com',
		    [self.user.email],
		    fail_silently=False,
		)
		return

	def minus(self,value):
		self.balance -= value
		self.save()
		notify.send(self.user, recipient=self.user, verb='$'+str(value)+' has been deducted to your wallet')
		send_mail(
		    '$'+str(value)+' has been deducted to your wallet',
		    'Hello ' + self.user.username + '. This is to notify you that $'+str(value)+' has recently been deducted to your wallet',
		    'system@solveware.com',
		    [self.user.email],
		    fail_silently=False,
		)
		return
	def getBalance(self):
		return self.balance

	def __str__(self):
		return '%s\'s Wallet' %(self.user.username)

	def getHistory(self):
		TodayDate = timezone.localtime(timezone.now()).date()
		t_set = Transaction.objects.filter(Q(senderID=self.user) | (Q(receiverID=self.user) & ~Q(status=Transaction.HG)), timestamp__gte = (TodayDate - timedelta(days=30))).order_by('-timestamp')
		return t_set


class BookingManager(models.Manager):
	def getRelatedBooking(self, own, sessionDate):
		relatedBooking = Booking.objects.filter(Q(status="not yet begun") | Q(status="locked")| Q(status="completed"), Q(tutorID = own) | Q(studentID = own), sessionDate = sessionDate)
		return relatedBooking

class Booking(models.Model):
	studentID = models.ForeignKey(myUser, related_name='b_student', on_delete=models.CASCADE)
	tutorID = models.ForeignKey(myUser, related_name='b_tutor', on_delete=models.CASCADE)
	sessionDate = models.DateField(auto_now_add=False)
	startTime = models.TimeField(auto_now_add=False)
	endTime = models.TimeField(auto_now_add=False)
	timestamp = models.DateTimeField(default = timezone.now)
	tutoringFee = models.FloatField(default=0, null=True)
	totalPayable = models.FloatField(default=0, null=True)
	commission = models.FloatField(default=0, null=True)
	#status = "not yet begun","locked", "end", "cancelled"
	status = models.CharField(max_length=20)

	objects = BookingManager()

	isReivew = models.BooleanField(default=False)

	def __str__(self):
		return '%s booked %s' %(self.studentID.user.username, self.tutorID.user.username)
	def createPayment(self):
		company = User.objects.get(username = "mytutors")

		p = Payment.objects.create_payment(self.studentID.user, company, self.id, self.totalPayable, Payment.TP)
		payflag = p.makePayment()
		if (payflag == False):
			return False
		else:
			return payflag
	def CanCancel(self):
		tz = pytz.timezone('Asia/Hong_Kong')
		bookingDateTime = datetime.combine(self.sessionDate, self.startTime)
		dkbookingDateTime = tz.localize(bookingDateTime, is_dst=True)
		if ((self.status == "not yet begun") and (dkbookingDateTime > timezone.localtime(timezone.now())+timedelta(hours=24))):
			print "can cancel"
			return True
		else:
			print "cannot cancel"
			return False
		

	def end(self):
		self.status = "ended"
		self.save()
		p = Payment.objects.get(bookingID=self.id)
		p.complete()
		send_mail(
	    'Review Invitation',
	    'Hello '+self.studentID.user.username+'. How is your experience in the tutorial session with ' + self.tutorID.user.username + ' ? Submit a review to rate your experience following this link: http://localhost:8000/'+self.id+'/review/',
	    'system@solveware.com',
	    [self.studentID.user.email],
	    fail_silently=False,
		)


	def cancel(self):
		self.status = "cancelled"
		self.save()
		notify.send(self.tutorID.user, recipient=self.tutorID.user, verb='Booking'+ self.bookingID + 'has been cancelled.' )
		notify.send(self.studentID.user, recipient=self.studentID.user, verb='Booking'+ self.bookingID + 'has sucessfully been cancelled.' )
		send_mail(
	    'Booking cancellation',
	    'Booking has been cancelled.',
	    'system@solveware.com',
	    ['test@solveware.com'],
	    fail_silently=False,
		)



class TransactionManager(models.Manager):
	def create_transaction(self, senderID, receiverID, transactionAmount, bookingID, action):
		t = self.create(senderID=senderID, receiverID=receiverID, transactionAmount=transactionAmount, bookingID=bookingID, action=action)
		t.begin()
		return t


class Transaction(models.Model):
	timestamp = models.DateTimeField(default = timezone.localtime(timezone.now()))
	AV = "Add Value"
	TP = "Tutorial Payment"	
	TS = "Tutorial Salary"
	HG = "Holding up by MyTutor"
	TD = "Transferred"
	CN = "Cancelled"
	WL = 'Withdrawl'
	choices = (
		(AV, 'Add Value'),
		(TP, 'Tutorial Payment'),
		(WL, 'Withdrawl'),
		)
	senderID = models.ForeignKey(User, related_name='senderID', on_delete=models.CASCADE, default = "")
	receiverID = models.ForeignKey(User, related_name='receiverID', on_delete=models.CASCADE, default = "")
	transactionAmount = models.FloatField()
	bookingID = models.ForeignKey(Booking, on_delete=models.CASCADE, blank=True, null=True)
	action = models.CharField(
		max_length=30,
		choices = choices,
		)
	STATUSCHOICES = (
		(HG, 'Holding up by MyTutor'),
		(TD, 'Transferred'),
		(CN, 'Cancelled'),
		)
	status= models.CharField(
		max_length=30,
	    choices=STATUSCHOICES,
	    default=HG,
		)

	objects = TransactionManager()

	def __str__(self):
		return '%s to %s : %s : %s' %(self.senderID.username, self.receiverID.username, self.action, self.status)
	def begin(self):
		self.senderID.wallet.minus(self.transactionAmount)
	def complete(self):
		self.status = Transaction.TD
		self.save()
		company = User.objects.get(username="mytutors")
		company.wallet.add(self.bookingID.commission)
		self.receiverID.wallet.add(self.bookingID.tutoringFee)

	def cancel(self):
		self.bookingID.cancel()
		self.status = Transaction.CN
		self.save()

class CourseCatalogue(models.Model):
	courseCode = models.CharField(max_length=8, default="") #in format: COMP1234
	courseName = models.CharField(max_length=50, default="")
	def __str__(self):
		return '%s' %(self.courseCode)
	def getCourseName(self):
		return '%s' %(self.courseName)

class CourseManager(models.Manager):
	def getCourse(self, tutorID):
		return Course.objects.filter(tutorID = tutorID)


class Course(models.Model):
	tutorID = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	courseCode = models.ForeignKey(CourseCatalogue, related_name='CC_CourseCode', on_delete=models.CASCADE, default = "")
	objects = CourseManager()
	def getCode(self):
		return self.course.courseCode
	



class Tag(models.Model):
	tutorID = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	tag = models.CharField(max_length=20)


class CouponManager(models.Manager):
	def isCouponValid(self, inputcode):		
		results = self.filter(couponCode = inputcode, startDateTime__lte = timezone.localtime(timezone.now()), endDateTime__gte = timezone.localtime(timezone.now()))
		return results
		#return JsonResponse(data=list(results.values()), safe=False)

class Coupon(models.Model):
	couponCode = models.CharField(max_length=10, default="")
	startDateTime = models.DateTimeField(auto_now_add = False, default = timezone.now)
	endDateTime = models.DateTimeField(auto_now_add = False, default = timezone.now)
	objects = CouponManager()
	def __str__(self):
		return '%s' %(self.couponCode)

class Review(models.Model):
	tutorID = models.ForeignKey(Tutor,on_delete=models.CASCADE, default="")
	studentID = models.ForeignKey(Student,on_delete=models.CASCADE, default="")
	bookingID = models.OneToOneField(Booking,on_delete=models.CASCADE, default="")
	description = models.TextField(default="")
	rate = models.FloatField(default=0, null=True)
	timestamp = models.DateTimeField(default = timezone.now)


	def __str__(self):
		return '%s' %(self.bookingID.id)

class BlackoutManager(models.Manager):
	def create_blackout(self, tutorID, date, startTime, endTime):
		blackout = self.create(tutorID=tutorID, date=date, startTime=startTime, endTime=endTime)
		return blackout
	def getBlackOutTutorDate(self, tutorID, Date):
		return Blackout.objects.filter(tutorID = tutorID, date = Date)
	def getBlackOutTutorDateTime(self, tutorID, Date, startTime):
		result = Blackout.objects.filter(tutorID = tutorID, date = Date, startTime = startTime)
		return result


class Blackout(models.Model):
	tutorID = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	date = models.DateField(auto_now_add=False)
	startTime = models.TimeField(auto_now_add=False)
	endTime = models.TimeField(auto_now_add=False)
	objects = BlackoutManager()

class PaymentManager(models.Manager):
	def create_payment(self, senderID, receiverID, bookingID, totalPayable, ptype):
		payment = self.create(senderID=senderID, receiverID=receiverID, bookingID=bookingID, totalPayable=totalPayable, ptype=ptype)
		return payment

class Payment(models.Model):
	senderID = models.ForeignKey(User, related_name='p_senderID', on_delete=models.CASCADE, default = "")
	receiverID = models.ForeignKey(User, related_name='p_receiverID', on_delete=models.CASCADE, default = "")
	bookingID = models.ForeignKey(Booking, related_name='p_bookingID', on_delete=models.CASCADE, null=True, default = "")
	totalPayable = models.FloatField(null=False)
	TP = "Tutorial Payment"
	PG = 'Processing'
	CD = 'Completed'
	PAYMENTCHOICES = (
		(TP, 'Tutorial Payment'),
		)
	ptype = models.CharField(
        max_length=30,
        choices=PAYMENTCHOICES,
        default=TP,
    )
	STATUSCHOICES = (
		(PG, 'Processing'),
		(CD, 'Completed')
	)
	status= models.CharField(
		max_length=30,
	    choices=STATUSCHOICES,
	    default=PG,
		)
	objects = PaymentManager()
	def makePayment(self):
		#get mytutor user instance
		print ("makePayment")

		if (Wallet.objects.pay(self.senderID, self.totalPayable) == True):
			print ("pay returns True")
			Wallet.objects.receive(self.receiverID, self.totalPayable)			
			return self
		else:
			print ("pay returns False")
			return False
	def createTransaction(self):
		t = Transaction.objects.create_transaction(self.senderID, self.receiverID, self.totalPayable, self.bookingID, Transaction.TP)
		t.save()
	def complete(self):
		self.status = Payment.CD
		self.save()
		t = Transaction.objects.get(bookingID=self.bookingID)
		t.complete()





