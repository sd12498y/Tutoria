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

class StudentManager(models.Manager):
	def create_student(self, user, university):
		student = self.create(user=user, university=university)
		return student
	def getRelatedBooking(self, sessionDate):
		relatedBooking = Booking.objects.filter(Q(status="not yet begun") | Q(status="locked")| Q(status="completed"), sessionDate = sessionDate)
		return relatedBooking

class Student (models.Model):
	user = models.OneToOneField(myUser, on_delete=models.CASCADE)
	university = models.CharField(max_length=50)
	objects =StudentManager()

	def __str__(self):
		return '%s' % (self.user.user.username)


class TutorManager(models.Manager):
	def create_tutor(self, user, university, description):
		tutor = self.create(user=user, university=university, description=description)
		return tutor
	def getRelatedBooking(self, sessionDate):
		relatedBooking = Booking.objects.filter(Q(status="not yet begun") | Q(status="locked")| Q(status="completed"), tutorID = self.user, sessionDate = sessionDate)
		return relatedBooking


class Tutor(models.Model):
	
	user = models.OneToOneField(myUser, on_delete=models.CASCADE)
	university = models.CharField(max_length=50)
	description = models.TextField()
	
	#objects = TutorManager()
	objects = InheritanceManager()

	def __str__(self):
		return '%s' % (self.user.user.username)
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
			
	def addValue(self,value):
		self.balance += value
		self.save()
		t = Transaction(payer=self.user, receiver=self.user, amount=value, action="Add Value")
		t.save()
		notify.send(self.user, recipient=self.user, verb='New value has been added to your wallet')
		send_mail(
		    'Value added to your wallet',
		    'Here is the message.',
		    'system@solveware.com',
		    ['s030046@gmail.com'],
		    fail_silently=False,
		)
		return
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

	def getBalance(self):
		return self.balance

	def __str__(self):
		return '%s\'s Wallet' %(self.user.username)

	def getHistory(self):
		TodayDate = timezone.localtime(timezone.now()).date()
		t_set = Transaction.objects.filter(Q(senderID=self.user) | Q(receiverID=self.user), timestamp__gte = (TodayDate - timedelta(days=30))).order_by('-timestamp')
		return t_set



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


class TransactionManager(models.Manager):
	def create_transaction(self, senderID, receiverID, transactionAmount, bookingID, action):
		t = self.create(senderID=senderID, receiverID=receiverID, transactionAmount=transactionAmount, bookingID=bookingID, action=action)
		return t


class Transaction(models.Model):
	timestamp = models.DateTimeField(default = timezone.localtime(timezone.now()))
	AV = "Add Value"
	RD = "Refund"
	TP = "Tutorial Payment"	
	TS = "Tutorial Salary"
	choices = (
		(AV, 'Add Value'),
		(RD, 'Refund'),
		(TP, 'Tutorial Payment'),
		)
	senderID = models.ForeignKey(User, related_name='senderID', on_delete=models.CASCADE, default = "")
	receiverID = models.ForeignKey(User, related_name='receiverID', on_delete=models.CASCADE, default = "")
	transactionAmount = models.FloatField()
	bookingID = models.ForeignKey(Booking, on_delete=models.CASCADE, blank=True, null=True)
	action = models.CharField(
		max_length=30,
		choices = choices,
		)

	objects = TransactionManager()


	def __str__(self):
		return '%s to %s : %s' %(self.payer.user.username, self.receiver.user.username, self.action)

class CourseCatalogue(models.Model):
	courseCode = models.CharField(max_length=8, default="") #in format: COMP1234
	courseName = models.CharField(max_length=50, default="")
	def __str__(self):
		return '%s' %(self.courseCode)
	def getCourseName(self):
		return '%s' %(self.courseName)


class Course(models.Model):
	tutorID = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	courseCode = models.ForeignKey(CourseCatalogue, related_name='CC_CourseCode', on_delete=models.CASCADE, default = "")
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
	studentID = models.ForeignKey(Student, related_name='r_student', on_delete=models.CASCADE)
	tutorID = models.ForeignKey(Tutor, related_name='r_tutor', on_delete=models.CASCADE)
	description = models.TextField(default="")
	rate = models.FloatField(default=0, null=True)

class BlackoutManager(models.Manager):
	def create_blackout(self, tutorID, date, startTime, endTime):
		blackout = self.create(tutorID=tutorID, date=date, startTime=startTime, endTime=endTime)
		return blackout

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
	PAYMENTCHOICES = (
		(TP, 'Tutorial Payment'),
		)
	ptype = models.CharField(
        max_length=2,
        choices=PAYMENTCHOICES,
        default=TP,
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





