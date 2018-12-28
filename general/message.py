from django.db.models import Q
from django.db.models import Count
from general.models import *
import pdb


def message_alert(request):
	if(request.user.id):
		message_alert = Message.objects.filter(customer_to=request.user, status='unread').count()
		return {
			'message_alert':message_alert,
		}
	else:
		return {
			'message_alert' : 0
		}