import json
import datetime

from django import template
from django.db.models import Avg
from django.utils import timezone

from general.models import *
from general.post_models import *

register = template.Library()

@register.filter
def raised_percent(campaign, css=False):
    percent = campaign.raised * 100 / campaign.budget
    if css and percent > 100:
        percent = 100
    return percent

@register.filter
def mul(value, arg):
    return value * arg

@register.filter
def ramained_days(campaign):
    return (campaign.created_at + datetime.timedelta(days=campaign.duration) - datetime.datetime.now().date()).days

@register.filter
def is_expired(campaign):
    return campaign.created_at + datetime.timedelta(days=campaign.duration) < datetime.datetime.now().date()

@register.filter
def get_vids(campaign):
    vids = [ii.strip() for ii in campaign.videos.split(',') if ii.strip()]
    return vids

@register.filter
def rating(customer):
    rate = Review.objects.filter(post__owner=customer).aggregate(Avg('rating')).values()[0]
    return rate if rate else 0

@register.filter
def rating_post(post):
    rate = Review.objects.filter(post=post).aggregate(Avg('rating')).values()[0]
    return rate if rate else 0

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + datetime.timedelta(n)

@register.filter
def disable_dates(post):
    d_days = []
    if post.category.form == 'ShortTermPost':
        for ii in json.loads(post.calendar):
            if not ii.get('avail', True):
                start_day = datetime.datetime.strptime(ii['start'], '%a %b %d %Y')
                end_day = datetime.datetime.strptime(ii['end'], '%a %b %d %Y')
                for single_date in daterange(start_day, end_day):
                    d_days.append(single_date.strftime("%Y-%m-%d"))
    return d_days

@register.filter
def rangee(start, end):
    return range(start, end+1)

@register.filter
def is_like(post, user):
    if user.is_authenticated():
        flag = Favourite.objects.filter(owner=user, post=post)
        return 'like' if flag else ''
    return ''

@register.filter
def address(post):
    if post.category.form == 'ShortTermPost':
        model = eval(post.category.form)
        post = model.objects.get(id=post.id)
        return '{} {}'.format(post.address, post.zip_code)
    return ''

@register.filter
def can_rate(purchase):
    flag = not purchase.udpated_at or purchase.udpated_at >= timezone.now() + datetime.timedelta(days=-30)
    flag = flag and not purchase.review_set.all()
    return flag

@register.filter
def head_sort_images(post):
    return post.images.all().order_by('-is_head')
