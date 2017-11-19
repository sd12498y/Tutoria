# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models import Q
from django.core.mail import send_mail
from notifications.signals import notify



class myUserManager(models.Manager):
	def create_myUser(self, user, tel, *propic):
		myUser = self.create(user=user, tel=tel, propic=propic)
		return myUser

class myUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	tel = models.CharField(max_length=8)
	propic = models.FileField(upload_to='static/img/propic/')

	objects = myUserManager()

	def __str__(self):
		return '%s' % (self.user.username)

class StudentManager(models.Manager):
	def create_student(self, user, school):
		student = self.create(user=user, school=school)
		return student

class Student (models.Model):
	user = models.OneToOneField(myUser, on_delete=models.CASCADE)
	school = models.CharField(max_length=50)
	objects =StudentManager()

	def __str__(self):
		return '%s' % (self.user.user.username)


class TutorManager(models.Manager):
	def create_tutor(self, user, school, description):
		tutor = self.create(user=user, school=school, description=description)
		return tutor

class Tutor(models.Model):
	CT = "Contract"
	PR = "Private"
	choices = (
		(CT, 'Contract'),
		(PR, 'Private'),
		)
	user = models.OneToOneField(myUser, on_delete=models.CASCADE)
	school = models.CharField(max_length=50)
	description = models.TextField()
	hourly_rate = models.IntegerField(default=0)
	tutor_type = models.CharField(max_length=20,
		choices=choices, default=PR)
	objects = TutorManager()

	def __str__(self):
		return '%s' % (self.user.user.username)

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
	user = models.OneToOneField(myUser, on_delete=models.CASCADE)
	balance = models.FloatField()

	def addValue(self,value):
		self.balance += value
		self.save()
		t = Transaction(payer=self.user, receiver=self.user, amount=value, action="Add Value")
		t.save()
		notify.send(self.user.user, recipient=self.user.user, verb='New value has been added to your wallet')
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
		notify.send(self.user.user, recipient=tutor.user, verb='Booking has been cancelled.' )
		notify.send(self.user.user, recipient=self.user.user, verb='Booking has sucessfully been cancelled.' )
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
		return '%s\'s Wallet' %(self.user.user.username)

	def getHistory(self):
		t_set = Transaction.objects.filter(Q(payer=self.user) | Q(receiver=self.user)).order_by('-timestamp')[:7]
		return t_set


class Booking(models.Model):
	student = models.ForeignKey(myUser, related_name='b_student', on_delete=models.CASCADE)
	tutor = models.ForeignKey(myUser, related_name='b_tutor', on_delete=models.CASCADE)
	session_date = models.DateField(auto_now_add=False)
	start_time = models.TimeField(auto_now_add=False)
	end_time = models.TimeField(auto_now_add=False)
	timestamp = models.DateTimeField(auto_now_add = True)
	tutoring_fee = models.FloatField(default=0, null=True)
	total_payable = models.FloatField(default=0, null=True)
	commission = models.FloatField(default=0, null=True)
	#status = "not yet begun","locked", "end", "cancelled"
	status = models.CharField(max_length=20)
	def __str__(self):
		return '%s booked %s' %(self.student.user.username, self.tutor.user.username)


class TransactionManager(models.Manager):
	def create_transaction(self, payer, receiver, amount, booking_id, action, timestamp):
		t = self.create(payer=payer, receiver=receiver, amount=amount, booking_id=booking_id, action=action, timestamp=timestamp)
		return t

class Transaction(models.Model):
	AV = "Add Value"
	RD = "Refund"
	IP = "Incoming Payment"
	OP = "Outgoing Payment"
	choices = (
		(AV, 'Add Value'),
		(RD, 'Refund'),
		(IP, 'Incoming Payment'),
		(OP, 'Outgoing Payment'),
		)
	payer = models.ForeignKey(myUser, related_name='payer', on_delete=models.CASCADE)
	receiver = models.ForeignKey(myUser, related_name='receiver', on_delete=models.CASCADE)
	amount = models.FloatField()
	booking_id = models.ForeignKey(Booking, on_delete=models.CASCADE, blank=True, null=True)
	action = models.CharField(
		max_length=30,
		choices = choices,
		)
	timestamp = models.DateTimeField(auto_now_add=True)

	objects = TransactionManager()


	def __str__(self):
		return '%s to %s : %s' %(self.payer.user.username, self.receiver.user.username, self.action)

class Course(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	course = models.CharField(max_length=8) #in format: COMP1234

class Tag(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	tag = models.CharField(max_length=20)

