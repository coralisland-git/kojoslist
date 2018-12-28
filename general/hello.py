from django.db.models import Q
from django.db.models import Count
from general.models import *
import pdb


def say_hello(request):
	message_alert = Message.objects.filter(customer_to=request.user, status='unread').count()
	return {
		'message_alert':message_alert,
	}