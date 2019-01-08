import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import *
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pdb


def send_email(from_email, subject, to_email, content):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_KEY)

    from_email = Email(from_email, "GlobalBoardWorld")
    to_email = Email(to_email)

    content = Content("text/html", content)
    mail = Mail(from_email, subject, to_email, content)
    return sg.client.mail.send.post(request_body=mail.get())

def send_SMS(to_phone, body):
    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    try:
        res = client.messages.create(
            to=to_phone,
            from_="+17069142868",
            body=body)  
    except TwilioRestException as e:
        print('~~~~~~~~~~~~~~~', e)

    return True

def send_email_Chat(from_email, subject, to_email, content, from_name):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_KEY)

    from_email = Email(from_email, from_name + " (GlobalBoardWorld)")
    to_email = Email(to_email)

    content = Content("text/html", content)
    mail = Mail(from_email, subject, to_email, content)
    return sg.client.mail.send.post(request_body=mail.get())

# def send_SMS_Chat(from_phone, to_phone, body):
#     client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

#     try:
#         res = client.api.account.messages.create(
#             to=to_phone,
#             from_=from_phone,
#             body=body)  
#     except Exception, e:
#         return False

#     return True