from django.db.models import Q
from django.db.models import Count
from general.models import *
import pdb


def message_alert(request):
	if(request.user.id):
		message_alert = 0
		messages = Message.objects.filter(customer_to=request.user, status='unread')
		temp = []
		for message in messages:
			if message.customer_from not in temp:
				temp.append(message.customer_from)
				message_alert += 1
		return {
			'message_alert':message_alert,
		}
	else:
		return {
			'message_alert' : 0
		}