# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.db.models.signals import post_save
from django.conf import settings

from general.models import *
from general.post_models import *

from general.utils import send_email
import pdb
from pytz import timezone

@receiver(pre_delete, sender=Image, dispatch_uid='image_delete_signal')
def delete_image_file(sender, instance, using, **kwargs):
    try:
        os.remove(settings.BASE_DIR+'/static/media/'+instance.name)
    except Exception, e:
        print e, '@@@@@ Error in delete_image_file()'

@receiver(post_save, sender=Post)
@receiver(post_save, sender=JobPost)
@receiver(post_save, sender=GaragePost)
@receiver(post_save, sender=SaleGarage)
@receiver(post_save, sender=CarPost)
@receiver(post_save, sender=MotorCyclePost)
@receiver(post_save, sender=BoatPost)
@receiver(post_save, sender=TrailerPost)
@receiver(post_save, sender=AptPost)
@receiver(post_save, sender=SubletPost)
@receiver(post_save, sender=AntiquePost)
@receiver(post_save, sender=CellPhonePost)
@receiver(post_save, sender=BookPost)
@receiver(post_save, sender=CDPost)
@receiver(post_save, sender=TicketPost)
@receiver(post_save, sender=AutoWheelPost)
@receiver(post_save, sender=RealEstatePost)
@receiver(post_save, sender=RoomPost)
@receiver(post_save, sender=OfficePost)
@receiver(post_save, sender=BuyGigPost)
@receiver(post_save, sender=LicensePost)
@receiver(post_save, sender=ShortTermPost)
def apply_subscribe(sender, instance, **kwargs):   
    try:
        for ss in Search.objects.filter(alert=True).exclude(owner=instance.owner):
            isApply = not ss.keyword or ss.keyword.lower() in instance.title.lower()
            if not ss.search_title and ss.keyword:
                isApply = isApply or ss.keyword.lower() in instance.content.lower()
            isApply = isApply and (ss.city == instance.region or ss.state == instance.region.state or ss.city == instance.region.district)
            isApply = isApply and (ss.category == instance.category or ss.category == instance.category.parent)
            if ss.has_image:
                isApply = isApply and instance.images.count() > 0

            if instance.price != None and ss.min_price != None:
                isApply = isApply and ss.min_price <= instance.price                
            if instance.price != None and ss.max_price != None:
                isApply = isApply and ss.max_price >= instance.price                

            if isApply:
                subscription_info = ''

                content = """
                    1 new result for your subscription ( {1} ) as of {2}<br><br>
                    <a href="{0}/ads/{3}">{4}</a><br><br>
                    <a href="{0}/my-subscriptions">See all of your subscriptions.</a><br><br>
                    Thank you for using <a href="http://{0}/">Globalboard</a>.                         
                """.format(settings.MAIN_URL, ss.category.name, str(instance.created_at), instance.id, instance.title)
                send_email(settings.FROM_EMAIL, 'Globalboard Subscription Alarm', ss.owner.email, content)
    except Exception, e:
        print e, '@@@@@ Error in apply_subscribe()'

@receiver(post_save, sender=Review)
def rating_notify(sender, instance, **kwargs):    
    try:
        content = '<a href="{0}/user_show/{1}">{2} {3}</a> left review on your ads (<a href="{0}/ads/{6}">{4}</a>) on {5}'.format(settings.MAIN_URL,
            instance.rater.id, instance.rater.first_name, instance.rater.last_name, 
            instance.post.title, instance.created_at.strftime("%b-%d-%Y at %H:%M%p"), instance.post.id)
        content += "<br><br>"+instance.content
        send_email(settings.FROM_EMAIL, 'Globalboard Rating Notification', instance.post.owner.email, content)
    except Exception, e:
        print e, '@@@@@ Error in rating_notify()'

@receiver(post_save, sender=PostPurchase)

def post_purchase_notify(sender, instance, **kwargs):    
    try:
        # send email to the owner

        subject = ''

        if instance.type == 'direct':
            subject = 'Item {0} purchased directly'.format(instance.post.title)
        else:
            subject = 'Item {0} purchased via escrow'.format(instance.post.title)
                       
        if instance.type == 'escrow' and instance.paid_percent != 100 and instance.status == 0:

            subject = 'Item {0} cancelled via escrow'.format(instance.post.title)

            content = "The transaction <a href='{0}/ads/{1}'>{2}</a> (${3}) has been cancelled by {4} {5} on {6}" \
                  .format(settings.MAIN_URL, instance.post.id, instance.post.title, instance.post.price,
                          instance.purchaser.first_name, instance.purchaser.last_name, instance.created_at.strftime("%b-%d-%Y at %H:%M%p"))

            content += "<br><br>Total Price: ${0}<br>Received Amount: ${2}({3}%)<br> Cancelled Amount: ${4}<br>Service Fee: ${1}<br>Total Amount Received: <span style='color: red'>${5}</span>" \
                        .format(instance.post.price, instance.post.price * settings.APP_FEE, instance.post.price * instance.paid_percent / 100.0, instance.paid_percent , instance.post.price * (1.0 - (instance.paid_percent / 100.0)), instance.post.price * (instance.paid_percent / 100.0 - settings.APP_FEE) )

            content += "<br><br>Contact Info:<br>" + instance.contact

            content_to_self = "You have cancelled the transaction <a href='{0}/ads/{1}'>{2}</a> (${3}) on {4}" \
                        .format(settings.MAIN_URL, instance.post.id, instance.post.title, instance.post.price,
                               instance.created_at.strftime("%b-%d-%Y at %H:%M%p"))

            content_to_self += "<br><br>Total Price: ${0}<br> Paid Amount: ${2}({3}%)<br> Cancelled Amount: ${4}<br>Service Fee: ${1}<br>Total Amount Paid: <span style='color: red'>${5}</span>" \
                        .format(instance.post.price, instance.post.price * settings.APP_FEE_BUY, instance.post.price * instance.paid_percent / 100.0, instance.paid_percent, instance.post.price * (1.0 - (instance.paid_percent / 100.0)), instance.post.price * (instance.paid_percent / 100.0 + settings.APP_FEE_BUY) )

            content_to_self += "<br><br>Contact Info:<br>{0} {1}".format(instance.post.owner.email, instance.post.owner.address)

        elif instance.type == 'escrow' and instance.paid_percent > 0:

            subject =  '{0}% item {1} purchased via escrow'.format(instance.paid_percent, instance.post.title)

            content = "{7}% of <a href='{0}/ads/{1}'>{2}</a> (${3}) has been purchased by {4} {5} on {6}" \
                  .format(settings.MAIN_URL, instance.post.id, instance.post.title, instance.post.price,
                          instance.purchaser.first_name, instance.purchaser.last_name, instance.created_at.strftime("%b-%d-%Y at %H:%M%p"), instance.paid_percent)
            
            content += "<br><br>Service Fee: ${0}<br>Total Amount Received: <span style='color: red'>${1}</span>" \
                        .format(instance.post.price * settings.APP_FEE, instance.post.price * (instance.paid_percent / 100.0 - settings.APP_FEE) )

            content += "<br><br>Contact Info:<br>"+instance.contact

            content_to_self = "You have purchased {5}% of <a href='{0}/ads/{1}'>{2}</a> (${3}) on {4}" \
                      .format(settings.MAIN_URL, instance.post.id, instance.post.title, instance.post.price,
                               instance.created_at.strftime("%b-%d-%Y at %H:%M%p"), instance.paid_percent)

            content_to_self += "<br><br>Service Fee: ${0}<br>Total Amount Paid: <span style='color: red'>${1}</span>" \
                        .format(instance.post.price * settings.APP_FEE_BUY, instance.post.price * (instance.paid_percent / 100.0 + settings.APP_FEE_BUY) )

            content_to_self += "<br><br>Contact Info:<br>{0} {1}".format(instance.post.owner.email, instance.post.owner.address)

        else:

            content = "<a href='{0}/ads/{1}'>{2}</a> (${3}) has been purchased {7} by {4} {5} on {6}<br><br>Contact Info:<br>" \
                  .format(settings.MAIN_URL, instance.post.id, instance.post.title, instance.post.price,
                          instance.purchaser.first_name, instance.purchaser.last_name, instance.created_at.strftime("%b-%d-%Y at %H:%M%p"), "" if instance.type == "direct" else "via escrow")

            content += instance.contact


            content_to_self = "You purchased a <a href='{0}/ads/{1}'>{2}</a> (${3}) {5} on {4}" \
                  .format(settings.MAIN_URL, instance.post.id, instance.post.title, instance.post.price,
                        instance.created_at.strftime("%b-%d-%Y at %H:%M%p"), "" if instance.type == "direct" else "via escrow")

            content_to_self += "<br><br>Contact Info:<br>{0} {1}".format(instance.post.owner.email, instance.post.owner.address)
            
        send_email(settings.FROM_EMAIL, subject, instance.post.owner.email, content)

        send_email(settings.FROM_EMAIL, subject, instance.purchaser.email, content_to_self)


    except Exception, e:

        print e, '@@@@@ Error in post_purchase_notify()'
