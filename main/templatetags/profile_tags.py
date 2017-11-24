# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.html import format_html
from django.contrib.auth.models import User
from django import template

register = template.Library()

@register.assignment_tag
def isStudent(user):
	if hasattr(user.myuser, 'student') == False:
		return False
	else:
		return True

@register.assignment_tag
def isTutor(user):
	if hasattr(user.myuser, 'tutor') == False:
		return False
	else:
		return True

@register.assignment_tag	
def getType(user):
	if hasattr(user.myuser.tutor, 'privatetutor') == False:
		return "Contract Tutor"
	else:
		return "Private Tutor"