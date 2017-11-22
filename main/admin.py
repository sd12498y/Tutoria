# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import myUser,Tutor,PrivateTutor, ContractTutor, Student,Wallet,Transaction,Booking,Tag,Course, CourseCatalogue, Review

admin.site.register(myUser)
admin.site.register(Tutor)
admin.site.register(PrivateTutor)
admin.site.register(ContractTutor)
admin.site.register(Student)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Booking)
admin.site.register(Tag)
admin.site.register(Course)
admin.site.register(CourseCatalogue)
admin.site.register(Review)

