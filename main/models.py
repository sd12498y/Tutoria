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

class Wallet(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	balance = models.FloatField()

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
		t = Transaction(payer=self.user , receiver=self.user, amount=value, action="Refund")
		t.save()
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
		t_set = Transaction.objects.filter(Q(payer=self.user) | Q(receiver=self.user)).order_by('-timestamp')[:7]
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


class TransactionManager(models.Manager):
	def create_transaction(self, payer, receiver, amount, booking_id, action, timestamp):
		t = self.create(payer=payer, receiver=receiver, amount=amount, booking_id=booking_id, action=action, timestamp=timestamp)
		return t

class Transaction(models.Model):
	timestamp = models.DateTimeField(default = timezone.now)
	AV = "Add Value"
	RD = "Refund"
	TP = "Tutorial Payment"
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
	def getValidCoupon(self):		
		results = self.filter(startDateTime__lte = timezone.localtime(timezone.now()), endDateTime__gte = timezone.localtime(timezone.now()))
		return results
		#return JsonResponse(data=list(results.values()), safe=False)

class Coupon(models.Model):
	couponCode = models.CharField(max_length=10, default="")
	startDateTime = models.DateTimeField(auto_now_add = False, default = timezone.now)
	endDateTime = models.DateTimeField(auto_now_add = False, default = timezone.now)
	objects = CouponManager()
	def __str__(self):
		return '%s' %(self.CouponCode)

class Review(models.Model):
	studentID = models.ForeignKey(Student, related_name='r_student', on_delete=models.CASCADE)
	tutorID = models.ForeignKey(Tutor, related_name='r_tutor', on_delete=models.CASCADE)
	description = models.TextField(default="")
	rate = models.FloatField(default=0, null=True)
	