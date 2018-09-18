import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import *
from twilio.rest import Client

def send_email(from_email, subject, to_email, content):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_KEY)

    from_email = Email(from_email, "Globalboard")
    to_email = Email(to_email)

    content = Content("text/html", content)
    mail = Mail(from_email, subject, to_email, content)
    return sg.client.mail.send.post(request_body=mail.get())

def send_SMS(to_phone, body):
    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

    try:
        res = client.api.account.messages.create(
            to=to_phone,
            from_="+1(201) 371-7692",
            body=body)  
    except Exception, e:
        return False

    return True