# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys
import json
import stripe
import datetime

from PIL import Image as PilImage

from random import randint

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth import logout
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q
from django.db.models import Count
from django.apps import apps
from allauth.socialaccount.models import *

from general.models import *
from general.post_models import *
from general.forms import *
from general.utils import send_email, send_SMS, send_email_Chat
import paypalrestsdk
from coinbase.wallet.client import Client
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
import math
from difflib import SequenceMatcher
import pdb
import geocoder
from datetime import timedelta


import pusher

pusher_client = pusher.Pusher(
  app_id='679333',
  key='febd0a7de92446f7f536',
  secret='0bbb6f04246f20dd62f9',
  cluster='mt1',
  ssl=True
)


get_class = lambda x: globals()[x]
stripe.api_key = settings.STRIPE_KEYS['API_KEY']

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": settings.PAYPAL_CLIENT,
  "client_secret": settings.PAYPAL_CLIENT_SECRET })

paypalrestsdk.configure({
  "mode": "live", # sandbox or live
  "client_id": settings.PAYPAL_CLIENT_LIVE,
  "client_secret": settings.PAYPAL_CLIENT_SECRET_LIVE })

client = Client(settings.BITCOIN_CLIENT, settings.BITCOIN_CLIENT_SECRET)

# def index(request):
#     next = request.GET.get('q', '/home')
#     return render(request, 'wraper.html', { 'next': next })

def index(request):
    # rndr_str = globoard_display_world_countries()
    # return render(request, 'index.html', {'rndr_str': rndr_str})
    # next = request.GET.get('q', '/home')
    # pdb.set_trace()
    # return render(request, 'wraper.html', { 'next': next })
    # if request.user.id is not None:
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def faq(request):
    return render(request, 'faq.html')

def how_it_works(request):
    return render(request, 'how-it-works.html')

def contact_us(request):
    return render(request, 'contact-us.html')

def customer_support(request):
    return render(request, 'customer-support.html')

def why_global_board(request):
    return render(request, 'why-global-board.html')

def terms_of_use(request):
    return render(request, 'terms-of-use.html')

def why_use(request):
    return render(request, 'why-use.html')

@login_required(login_url='/accounts/login/')
def my_ads(request):
    posts = Post.objects.filter(owner=request.user, available=True).order_by('-created_at')
    posts = get_posts_with_image(posts, True)
    return render(request, 'my-ads.html', {'posts': posts})

@csrf_exempt
def search_ads(request):
    keyword = request.POST.get('keyword')
    model = request.POST.get('model')
    others = request.POST.get('others') == 'true'
    view_mode = request.POST.get('view_mode')
    is_world = request.POST.get('is_world') == 'True'
    region = request.session.get('region')
    # category = request.POST.get('category')

    q = ( Q(title__icontains=keyword) | Q(tag__icontains=keyword) )
    if 'ck_search_title' not in request.POST:
        q = (Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(tag__icontains=keyword))

    if region and not is_world:
        q &= (Q(region_id=region) | Q(region__district__id=region) | Q(region__isnull=True))

    if not others:
        q &= Q(owner=request.user)

    for key, value in request.POST.iteritems():
        if value and key not in ['model', 'keyword', 'others', 'csrfmiddlewaretoken', 'view_mode', 'is_world'] \
        and key[:3] != 'ck_' and value != None:
            q &= Q(**{key: value})

    if model:   # search on specific category page
        q &= Q(category_id=request.session['category'])

    model = apps.get_model('general', model or 'Post')
    posts = model.objects.filter(q).exclude(status='deactive').order_by('-created_at')

    if 'ck_has_image' in request.POST:
        posts = posts.annotate(img_num=Count('images')).filter(img_num__gt=0).order_by('-created_at')
    if 'ck_posted_today' in request.POST:
        posts = posts.filter(created_at__gte=datetime.datetime.now().date()).order_by('-created_at')

    posts = get_posts_with_image(posts)
    rndr_str = render_to_string(view_mode, {'posts': posts, 'others': others}, request=request)
    return HttpResponse(rndr_str)

def get_posts_with_image(posts, mine=False):
    # add expiration filter here
    posts_with_image = []
    for post in posts:
        if post.status != 'expired' or mine:
            image = post.images.filter(is_head=True).first() or post.images.all().first()
            # need to be revised
            img_name = 'thumbnail-'+image.name if image else 'dummy.jpg'
            posts_with_image.append((post, img_name))
    return posts_with_image

def profile(request):
    if request.user.is_authenticated():
        # pass
        try:
            request.user.default_site = request.session['default_site']
            request.user.save()
        except:
            pass
    return render(request, 'profile.html', locals())

@csrf_exempt
def breadcrumb(request):
    session = get_session(request)
    mapName = request.POST.get('mapName')
    state = request.POST.get('state').replace('%27', "'") \
                                    .replace('%20', " ")
    is_state = request.POST.get('is_state')
    city = request.POST.get('city')
    kind = mapName.count('-')

    if city:
        city = City.objects.get(id=city)
        mapname = 'countries/{0}/{0}-all'.format(city.state.country.sortname.lower())
        smapname = mapName + '@' + city.state.name

        if city.district:   # district
            cmapname = smapname + '@' + str(city.district.id)
            dmapname = smapname + '@' + str(city.id)
            args = [mapname, city.state.country.name,
                    smapname, city.state.name,
                    cmapname, city.district.name,
                    dmapname, city.name]
        else:
            cmapname = smapname + '@' + str(city.id)
            args = [mapname, city.state.country.name,
                    smapname, city.state.name,
                    cmapname, city.name]

    elif kind == 2 or is_state == 'true': # - city
        country = mapName.split('/')[1].upper()
        state = State.objects.filter(name=state, country__sortname=country).first()
        cmapname = 'countries/{0}/{0}-all'.format(state.country.sortname.lower())
        mapname = mapName if '@' in mapName else mapName + '@' + state.name
        args = [cmapname, state.country.name,
                mapname, state.name]
    elif kind == 1: # state
        country = mapName.split('/')[1].upper()
        country = Country.objects.filter(sortname=country).first()
        args = [mapName, country.name]

    html = render_to_string('_breadcrumb.html', locals())
    put_session(request, 'breadcrumb', html)

    return HttpResponse(html)

def get_session(request):
    if not request.session.session_key:
        request.session.create()
    session, _ = CSession.objects.get_or_create(key=request.session.session_key)
    return session

def put_session(request, key, val):
    session = get_session(request)
    content = json.loads(session.val)
    content[key] = val
    session.val = json.dumps(content)
    session.save()

def retrieve_session(request, key, default):
    session = get_session(request)
    content = json.loads(session.val)
    return content.get(key, default)

def get_regions(request):
    """
    get regions like countries, states or cities
    and search link, list title
    """
    mapName = request.GET.get('mapName')
    state = request.GET.get('state').replace('%27', "'") \
                                    .replace('%20', " ")
    is_state = request.GET.get('is_state')
    city = request.GET.get('city')
    kind = mapName.count('-')

    # if request.user.is_authenticated():
    #     # store last location
    #     loc = mapName
    #     if kind == 2 or is_state == 'true':
    #         loc += '@' + state
    #     if city:
    #         loc += '@' + city
    #     request.user.default_site = loc
    #     request.user.save()

    request.session['category'] = ''

    if city:
        city = City.objects.get(id=city)
        link = '/region-ads/ct/{}'.format(city.id)
        request.session['region'] = city.id
        request.session['region_kind'] = 'city'

        title = 'Select Category'

        result = []
        for column in range(1, 7):
            _result = []
            for mc in Category.objects.filter(parent__isnull=True, column=column).order_by('order'):
                cc = Category.objects.filter(parent=mc).order_by('name')
                _result += [(mc, cc)]
            result += [_result]
        html = render_to_string('_category.html', {'categories': result})
    elif kind == 2 or is_state == 'true': # - city
        country = mapName.split('/')[1].upper()
        state = State.objects.filter(name=state, country__sortname=country).first()
        title = 'Select City'
        link = '' #'/region-ads/st/{}'.format(state.id)
        request.session['region'] = state.id
        request.session['region_kind'] = 'state'
        cities = City.objects.filter(state=state, district__isnull=True).order_by('name')
        html = render_to_string('_city_list.html', {'cities': cities})
    elif kind == 0: # country
        title = 'Select Country'
        link = ''# '/region-ads/'
        request.session['region'] = ''
        request.session['region_kind'] = 'world'

        html = render_to_string('_country_list_.html', {'countries': Country.objects.all()})
    elif kind == 1: # state
        country = mapName.split('/')[1].upper()
        country = Country.objects.filter(sortname=country).first()
        title = 'Select Region'
        link = ''#'/region-ads/{}'.format(country.id)
        request.session['region'] = country.id
        request.session['region_kind'] = 'country'

        html = render_to_string('_state_list.html',
                                {'states': State.objects.filter(country=country).order_by('name')})

    request.session.modified = True

    result = {
        'title': title,
        'link': link,
        'html': html
    }

    return JsonResponse(result, safe=False)

@login_required(login_url='/accounts/login/')
def post_ads(request, ads_id):
    if request.method == 'GET':
        stripe_connected = SocialAccount.objects.filter(user=request.user, provider='stripe').exists()
        mcategories = Category.objects.filter(parent__isnull=True).order_by('name')
        countries = Country.objects.all()
        skey = settings.STRIPE_KEYS['PUBLIC_KEY']

        if ads_id:
            post = Post.objects.get(id=ads_id)
            model = eval(post.category.form)
            post = model.objects.get(id=ads_id)
            if post.region:
                states = State.objects.filter(country=post.region.state.country)
                cities = City.objects.filter(state=post.region.state, district__isnull=True)

                districts = post.region.districts.all()
                if post.region.district:    # for districts
                    districts = post.region.district.districts.all()

            images = post.images.all()
            detail_template = 'post/{}.html'.format(post.category.form)
        else:
            post = {}       # just for form
            detail_template = 'post/Post.html'

            if request.user.default_site:
                if '/' in request.user.default_site:
                    country = request.user.default_site.split('/')[1].upper()
                else:
                    country = ''
                post['country'] = country       # country sortname
                states = State.objects.filter(country__sortname=country)
                loc = request.user.default_site.split('@')
                if len(loc) > 1:
                    state = loc[1]  # state name
                    post['state'] = state
                    cities = City.objects.filter(state__name=state, district__isnull=True)

                if len(loc) > 2:    # city id
                    city = City.objects.get(id=loc[-1])
                    districts = city.districts.all()
                    post['region_id'] = city.id

        return render(request, 'post_ads.html', locals())
    else:
        form_name = request.POST.get('ads_form') + 'Form'
        form = get_class(form_name)

        if ads_id:
            model = eval(request.POST.get('ads_form'))
            instance = model.objects.get(id=ads_id)
            form = form(request.POST, instance=instance)
        else:
            form = form(request.POST)

        # ignore last empty one due to template
        images = request.POST.getlist('uploded_id[]')[:-1]
        if form.is_valid():
            post = form.save()
            post.updated_at = datetime.datetime.now()
            post.save()

            pimages = [ii.name for ii in post.images.all()]

            # create objects for new images
            for img in list(set(images)-set(pimages)):
                Image.objects.create(post=post, name=img)

            # remove deleted ones
            for img in list(set(pimages)-set(images)):
                try:
                    os.remove(settings.BASE_DIR+'/static/media/'+img)
                except Exception:
                    pass
                Image.objects.filter(name=img).delete()

            # update head image
            head_url = request.POST.get('head_image').split('/')[-1]
            post.images.all().update(is_head=False)
            post.images.filter(name=head_url).update(is_head=True)

            price = post.price

            card = request.POST.get('stripeToken')
            if price and card:
                price = int(post.price * 100 * settings.APP_FEE)
                try:
                    stripe.Charge.create(
                        amount=price,
                        currency="usd",
                        source=card, # obtained with Stripe.js
                        description="Charge for Post(#{} - {})".format(post.id, post.title)
                    )
                    # pdb.set_trace()
                except Exception, e:
                    print e, 'stripe error ##'
        print(form.errors, '$$$$$$$$')
        return HttpResponseRedirect(reverse('my-ads'))

def ulogout(request):
    logout(request)
    return HttpResponseRedirect('/')

def get_sub_info(request):
    """
    ajax call for sub category, state, city
    """
    obj_id = request.GET.get('obj_id')
    sc_type = request.GET.get('type') # Category, State, City, District
    rndr_str = '<option value="">-Select-</option>'

    if sc_type == 'category':
        for cc in Category.objects.filter(parent__id=obj_id).order_by('name'):
            if cc.category_set.all():
                rndr_str += '<option value="" disabled>{}</option>'.format(cc.name)
                for sc in cc.category_set.all():
                    rndr_str += '<option value="{}">&nbsp;&nbsp;&nbsp;&nbsp;{}</option>'.format(sc.id, sc.name)
            else:
                rndr_str += '<option value="{}">{}</option>'.format(cc.id, cc.name)
        objects = []
    elif sc_type == 'state':
        objects = State.objects.filter(country__id=obj_id)
    elif sc_type == 'city':
        objects = City.objects.filter(state__id=obj_id, district__isnull=True)
    else:
        objects = City.objects.filter(district_id=obj_id)

    for sc in objects:
        rndr_str += '<option value="{}">{}</option>'.format(sc.id, sc.name)
    return HttpResponse(rndr_str)

@csrf_exempt
def upload_image(request):
    myfile = request.FILES['images']
    _type = request.POST.get('type', '')
    if _type:
        _type = _type + '/'

    fs = FileSystemStorage()
    filename = fs.save(_type+myfile.name, myfile)

    size = 128, 128
    try:
        x = float(request.POST.get('x'))
        y = float(request.POST.get('y'))
        w = float(request.POST.get('width'))
        h = float(request.POST.get('height'))
        image = PilImage.open(settings.BASE_DIR+'/static/media/'+filename)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((600, 600))
        resized_image.save(settings.BASE_DIR+'/static/media/'+filename)
        # im = PilImage.open(settings.BASE_DIR+'/static/media/'+filename)
        resized_image.thumbnail(size)
        resized_image.save(settings.BASE_DIR+'/static/media/thumbnail-'+filename)
    except IOError:
        print "cannot create thumbnail for", filename

    uploaded_file_url = fs.url(filename)
    res = { "image_url": uploaded_file_url,"image_name": uploaded_file_url.split('/')[-1] }
    return JsonResponse(res, safe=False)

@csrf_exempt
def delete_image(request):
    image_name = request.POST.get('image_name')
    # if not belong to any post
    if not Image.objects.filter(name=image_name):
        try:
            os.remove(settings.BASE_DIR+'/static/media/'+image_name)
        except Exception:
            pass
    return HttpResponse('')

def get_post_detail(request):
    obj_id = request.GET.get('obj_id')
    category = Category.objects.get(id=obj_id)
    form_name = category.form
    price = int(category.price * 100)
    template = 'post/{}.html'.format(form_name)
    html = render_to_string(template)

    return JsonResponse({
        'html': html,
        'form': form_name,
        'dealer_avail': category.column == 10,
        'price': price}, safe=False)

@csrf_exempt
def active_deactive_ads(request):
    ads = request.POST.get('ads_id')
    status = request.POST.get('status')
    Post.objects.filter(id=ads).update(status=status)
    return HttpResponse('')

@csrf_exempt
def delete_ads(request):
    ads = request.POST.get('ads_id')
    Post.objects.filter(id=ads).update(available=False)
    # Post.objects.filter(id=ads).delete()
    return HttpResponse('')

@csrf_exempt
def delete_camp(request):
    camp = request.POST.get('camp_id')
    Campaign.objects.filter(id=camp).delete()
    return HttpResponse('')

def view_ads(request, ads_id):
    post = get_object_or_404(Post, pk=ads_id)
    model = eval(post.category.form)
    post = model.objects.get(id=ads_id)
    activated = request.GET.get('activated')

    favourite = False
    result = ''
    optpay = ''
    lack_amount = 0
    flag = False

    if request.user.is_authenticated():
        posts = [ii.post.id for ii in Favourite.objects.filter(owner=request.user)]
        favourite = post.id in posts

    if request.method == 'POST':

        paypal_transaction_id = request.POST.get('paypal_transaction_id')
        optpay = request.POST.get('optpay')
        contact = request.POST.get('contact')
        bitcoin_transaction = request.POST.get('bitcoin_transaction')

        status = 1
        if optpay == 'direct':
            status = 0

        if paypal_transaction_id != '':

            check_purchase = PostPurchase.objects.filter(transaction=paypal_transaction_id)

            if len(check_purchase) == 0:

                # amount = post.price * ( 1 + settings.APP_FEE_BUY)
                # receiver_email = post.owner.paypal

                # payout = paypalrestsdk.Payout({
                #     "sender_batch_header": {
                #         "sender_batch_id": "batch",
                #         "email_subject": "You have a payment"
                #     },
                #     "items": [
                #         {
                #             "recipient_type": "EMAIL",
                #             "amount": {
                #                 "value": amount,
                #                 "currency": "USD"
                #             },
                #             "receiver": receiver_email,
                #             "note": "Thank you.",
                #             "sender_item_id": "item"
                #         }
                #     ]
                # })

                # if payout.create(sync_mode=False):
                #     print("payout[%s] created successfully" %
                #           (payout.batch_header.payout_batch_id))
                # else:
                #     print(payout.error)

                purchase = PostPurchase.objects.create(post=post,
                                                       purchaser=request.user,
                                                       type=optpay,
                                                       contact=contact,
                                                       status=status,
                                                       transaction=paypal_transaction_id)

                result = paypal_transaction_id

                flag = True

                print('~~~~~~~~~~~~~ purchased by paypal ~~~~~~~~~~~~~~~')


        elif bitcoin_transaction != '':

            check_purchase = PostPurchase.objects.filter(transaction=bitcoin_transaction)

            if len(check_purchase) == 0:

                my_transactions = client.get_transactions(settings.BITCOIN_ACCOUNT).data

                purchased_transactions = PostPurchase.objects.filter(transaction=bitcoin_transaction)

                if len(purchased_transactions) == 0:

                    for trans in my_transactions:

                        # if bitcoin_transaction == trans.network['hash'] and trans.status == "completed":

                        if bitcoin_transaction == trans.network['hash']:


                            # sent_amount = float(trans.native_amount['amount'])

                            # sent_currency = trans.native_amount['currency']

                            # c = CurrencyRates()

                            # res_amount = c.convert(sent_currency, 'USD', sent_amount)

                            # if res_amount >= post.price:

                            if trans.status == 'completed':

                                status = 0

                            else :

                                status = 3

                            purchase = PostPurchase.objects.create(post=post,
                                                                   purchaser=request.user,
                                                                   type='direct',
                                                                   contact=contact,
                                                                   status=status,
                                                                   transaction=bitcoin_transaction)

                            result = bitcoin_transaction

                            print('~~~~~~~~~~~~~ purchased by bitcoin ~~~~~~~~~~~~~~~')

                            flag = True
                            # return HttpResponseRedirect(reverse('view-ads', args=(ads_id,)))
                else:
                    message = "The transaction is not available. Try again, please."

        else:
            card = request.POST.get('stripeToken')
            amount = int(post.price * 100)

            if post.category.form == 'ShortTermPost':
                checkin = request.POST.get('checkin')
                checkout = request.POST.get('checkout')
                adults = request.POST.get('adults')
                children = request.POST.get('children')
                infants = request.POST.get('infants')
                checkin = datetime.datetime.strptime(checkin, '%m/%d/%Y')
                checkin = datetime.datetime.strftime(checkin, '%a %b %d %Y')
                checkout = datetime.datetime.strptime(checkout, '%m/%d/%Y')
                checkout = datetime.datetime.strftime(checkout, '%a %b %d %Y')

                calendar = json.loads(post.calendar)
                calendar.append({
                    'start': checkin,
                    'end': checkout,
                    'avail': False,
                    'color': '#ff9800',
                    'url': '{}/user_show/{}'.format(settings.MAIN_URL, request.user.id),
                    'title': '{} {} - {}/{}/{}'.format(request.user.first_name,
                                                     request.user.last_name,
                                                     adults,
                                                     children,
                                                     infants)
                })
                post.calendar = json.dumps(calendar)
                post.save()

            try:

                status = 0

                total_amount = int(math.ceil((settings.APP_FEE_BUY + 1)*post.price*100))

                charge = ''

                if optpay == "direct":
                    stripe_account_id = SocialAccount.objects.get(user=post.owner, provider='stripe').uid

                    try:

                        charge = stripe.Charge.create(
                            amount=total_amount,
                            currency="usd",
                            source=card, # obtained with Stripe.js
                            # destination=stripe_account_id,
                            # application_fee = int(amount * settings.APP_FEE_BUY),
                            description="Direct pay to the ads (#{} - {})".format(post.id, post.title)
                        )
                    except Exception as e:
                        print('~~~~~~~~~~', e)
                else:
                    charge = stripe.Charge.create(
                        amount=total_amount,
                        currency="usd",
                        source=card, # obtained with Stripe.js
                        # destination=stripe_account_id,
                        description="Escrow for the ads (#{} - {})".format(post.id, post.title)
                    )
                    status = 1  # under escrow

                result = charge.id
                purchase = PostPurchase.objects.create(post=post,
                                                       purchaser=request.user,
                                                       type=optpay,
                                                       contact=contact,
                                                       status=status,
                                                       transaction=charge.id)

                print('~~~~~~~~~~~~~ purchased by stripe ~~~~~~~~~~~~~~~')

                flag = True

            except Exception as e:
                print e, '@@@@@ Error in view_ads()'
    if flag:
        reviews = Review.objects.filter(post__id=ads_id)
    skey = settings.STRIPE_KEYS['PUBLIC_KEY']
    pkey = settings.PAYPAL_CLIENT
    pkey_live = settings.PAYPAL_CLIENT_LIVE
    if post.price:
        service_fee = math.ceil(settings.APP_FEE_BUY * post.price*100)/100
        total_amount = math.ceil((settings.APP_FEE_BUY + 1)*post.price*100)/100
        bc = BtcConverter()
        bitcoin_amount = bc.convert_to_btc_on(total_amount, 'USD', datetime.datetime.now() - datetime.timedelta(days=1))
    return render(request, 'ads_detail.html', locals())

def show_earlier_messages(request):
    count = int(request.GET.get('count'))
    client_id = request.GET.get('client_id')
    post_id = request.GET.get('post_id')
    client = Customer.objects.get(id=client_id)
    post = Post.objects.get(id=post_id)
    messages = Message.objects.filter(Q(customer_from=request.user, customer_to=client, post=post) | Q(customer_to=request.user, customer_from=client, post=post)).order_by('-date')
    end = False
    if len(messages) < count + 15:
        end = True

    if len(messages) > count:
        messages = messages[count: count + 15]
    else:
        messages = []
    count = count + len(messages)
    rndr_str = render_to_string("_more_messages.html" , {
                'messages': messages,
                'me' : request.user,
                'client' : client
                }, request=request)

    data = {
            'more_messages': rndr_str,
            'count' : count,
            'end' : end
        }
    return JsonResponse(data, safe=False)

@login_required(login_url='/accounts/login/')
def view_ads_message(request, ads_id, client_id):
    if client_id:
        post = get_object_or_404(Post, pk=ads_id)
        model = eval(post.category.form)
        post = model.objects.get(id=ads_id)
        # count = 10
        client = Customer.objects.get(id=client_id)
        # client = post.owner
        reviews = Review.objects.filter(post__owner=client) \
                               .values('post__category__name', 'post__category__parent__name',
                                       'post__category__id') \
                               .distinct().count()
        me = request.user
        messages = Message.objects.filter(Q(customer_from=request.user, customer_to=client, post=post) | Q(customer_to=request.user, customer_from=client, post=post)).order_by('-date')
        end = False
        if len(messages) <= 15:
            end = True
        messages = messages[:15]
        count = len(messages)

        if 'timeoffset' in request.session:
            for message in messages:
                message.date = (message.date - timedelta(minutes=int(request.session['timeoffset']))).strftime("%b. %d, %Y, %I:%M %P")
        return render(request, 'ads_detail_message.html', locals())
    else:
        # messages = Message.objects.filter(Q(customer_from=request.user) | Q(customer_to=request.user))
        post_id = ads_id
        me = request.user
        messages_starred = [] #len(Message.objects.filter(customer_to=request.user, status="starred"))
        messages_unread = [] #len(Message.objects.filter(customer_to=request.user, status="unread"))
        messages_sent = []
        messages_len = 0
        messages_unread_len = 0
        messages_reservations = 0 #len(Message.objects.filter(customer_from=request.user, status="starred"))
        messages_pending_requests = 0 #len(Message.objects.filter(customer_from=request.user, status="unread"))
        messages_sent_len = 0
        messages_archieve = []
        messages = []
        messages_s_all = Message.objects.filter(Q(customer_from=request.user)).order_by('-date')
        messages_s = []
        for message in messages_s_all:
            item = {'client' : message.customer_to, 'starred' : message.starred, 'archieve': message.archieve, 'post' : message.post}
            if item not in messages_s:
                messages_s.append(item)
        messages_r_all = Message.objects.filter(Q(customer_to=request.user)).order_by('-date')
        messages_r = []
        for message in messages_r_all:
            item = {'client' : message.customer_from, 'starred' : message.starred, 'archieve': message.archieve, 'post' : message.post}
            if item not in messages_r:
                messages_r.append(item)
        for message in messages_s:
            if message not in messages_r:
                messages_sent.append(message)
        messages_all = Message.objects.filter(Q(customer_to=request.user) | Q(customer_from=request.user)).order_by('-date')
        for message in messages_all:
            item_to = {'client' : message.customer_to, 'starred' : message.starred, 'archieve': message.archieve, 'post' : message.post}
            item_from = {'client' : message.customer_from, 'starred' : message.starred, 'archieve': message.archieve, 'post' : message.post}
            if message.archieve:
                if message.customer_from == request.user and item_to not in messages_archieve:
                    messages_archieve.append(item_to)
                if message.customer_to == request.user and item_from not in messages_archieve:
                    messages_archieve.append(item_from)
            else:
                if message.customer_from == request.user:
                    if item_to not in messages:
                        messages_len += 1
                        messages.append(item_to)
                if message.customer_to == request.user:
                    if item_from not in messages:
                        messages_len += 1
                        messages.append(item_from)
                if message.starred:
                    if message.customer_from == request.user and item_to not in messages_starred:
                        messages_starred.append(item_to)
                    if message.customer_to == request.user and item_from not in messages_starred:
                        messages_starred.append(item_from)
                if message.status == 'unread':
                    if message.customer_to == request.user:
                        if item_from not in messages_unread:
                            messages_unread_len += 1
                            messages_unread.append(item_from)
        messages_sent_len = len(messages_sent)
        messages_archieve_len = len(messages_archieve)
        messages_starred_len = len(messages_starred)
        message_alert = messages_unread_len
        # messages_len = len(messages)
        # messages_unread_len = len(messages_unread)
        messages_new = []
        for message in messages:
            if message in messages_unread:
                message['new'] = True
                messages_new.append(message)
        for message in messages:
            if message not in messages_new:
                messages_new.append(message)
        messages = messages_new
        status = request.GET.get('status')
        if 'status' in request.GET:
            if status == 'sent':
                messages = messages_sent
            if status == 'starred':
                messages = messages_starred
            if status == 'archieve':
                messages = messages_archieve
            if status == 'unread':
                for msg in messages_unread:
                    msg['new'] = True
                messages = messages_unread
            rndr_str = render_to_string("_sub_message_list.html" , {
                    'messages': messages
                    }, request=request)
            return HttpResponse(rndr_str)
        else:
            return render(request, 'ads_detail_message_all.html', locals())

@csrf_exempt
def send_reply_email(request):
    from_email = request.user.email
    content = request.POST.get('content')
    client_id = request.POST.get('client_id')
    post_id = request.POST.get('post_id')
    post = Post.objects.get(id=post_id)
    client = Customer.objects.get(id=client_id)
    room_infos = Message.objects.filter(Q(customer_from=request.user, post=post) | Q(customer_to=request.user, post=post) )
    room_starred= False
    room_archieve = False
    if len(room_infos) > 0:
        room_starred = room_infos[0].starred
        room_archieve = room_infos[0].archieve
    message = Message.objects.create(customer_from=request.user,
                           customer_to=client,
                           post=post,
                           content=content,
                           status="unread",
                           starred=room_starred,
                           archieve=room_archieve
                        )
    if 'timeoffset' in request.session:
        message.date = message.date - timedelta(minutes=int(request.session['timeoffset']))

    pusher_client.trigger('message-channel-'+str(request.user.id)+'-'+str(client.id),
                            'message-event-'+str(request.user.id)+'-'+str(client.id),
                            {
                                'mid' : message.id,
                                'message': content,
                                'date' : message.date.strftime("%b. %d, %Y, %I:%M %P")
                            }
                        )

    pusher_client.trigger('message-channel-'+str(client.id),
                            'message-event-'+str(client.id),
                            {
                                'message' : 'notification'
                            }
                        )
    subject = post.title
    content_email = """{1}
        <br><br>Post : <a href='{0}/ads/{2}'>{0}/ads/{2}</a>
        <br><br>Please Respond Here : <a href='{0}/ads-message/{2}/{3}'>{0}/ads-message/{2}/{3}</a>
        """.format(settings.MAIN_URL, content, post_id, request.user.id)

    from_name = request.user.first_name + ' ' + request.user.last_name

    content_sms = "GlobalBoardWorld: " + from_name + ", '" + content + "'"
    # ___send message___
    send_email_Chat(settings.FROM_EMAIL, subject, client.email, content_email, from_name)
    try:
        send_SMS(client.phone, content)
        # send_SMS('+1(978) 295-1387', content_sms)
        # send_SMS('12125184715', content_sms)
    except Exception as e:
        print('^^^^^^^^^^^^^^^^^', e)
    return HttpResponse('')

def change_status(request):
    if 'alert' in request.GET:
        if 'turnRead' in request.GET:
            post_id = request.GET.get('postId')
            client_id = request.GET.get('clientId')
            post = Post.objects.get(id=post_id)
            client = Customer.objects.get(id=client_id)
            messages_all = Message.objects.filter(Q(customer_from=request.user, customer_to=client, post=post) | Q(customer_to=request.user, customer_from=client, post=post)).order_by('-date')
            for message in messages_all:
                if message.status == 'unread' and message.customer_from != request.user:
                    message.status = 'read'
                    message.save()

        # message_alert = 0
        # messages_all = Message.objects.filter(Q(customer_to=request.user) | Q(customer_from=request.user))
        # for message in messages_all:
        #     if message.status == 'unread' and message.archieve == False :
        #         if message.customer_to == request.user:
        #             message_alert += 1
        message_alert = 0
        messages = Message.objects.filter(customer_to=request.user, status='unread')
        temp = []
        for message in messages:
            if message.customer_from not in temp:
                temp.append(message.customer_from)
                message_alert += 1
        return HttpResponse(message_alert)
    else:
        try:
            mid = request.GET.get('mid')
            message = Message.objects.get(id=mid)
            message.status = 'read'
            message.save()
        except:
            pass
        return HttpResponse('')
    # status = request.GET.get('status')
    # flag = True
    # messages = []
    # if status == '':
    #     messages_all = Message.objects.filter(Q(customer_to=request.user) | Q(customer_from=request.user), ~Q(status='archieve'))
    # # elif status == 'starred':
    # #     messages = Message.objects.filter(customer_to=request.user, status=status).group_by('customer_from').distinct()
    # # elif status == 'unread':
    # #     messages = Message.objects.filter(customer_to=request.user, status=status).group_by('customer_from').distinct()
    # # elif status == 'reservations':
    # #     flag = False
    # #     messages = Message.objects.filter(customer_from=request.user, status="starred").group_by('customer_to').distinct()
    # # elif status == 'pending_requests':
    # #     flag = False
    # #     messages = Message.objects.filter(customer_from=request.user, status="unread").group_by('customer_to').distinct()
    # elif status == 'archieve':
    #     messages_all = Message.objects.filter(Q(customer_to=request.user) | Q(customer_from=request.user), Q(status='archieve'))

    # for message in messages_all:
    #     if message.customer_from == request.user and message.customer_to not in messages:
    #         messages.append(message.customer_to)
    #     if message.customer_to == request.user and message.customer_from not in messages:
    #         messages.append(message.customer_from)

    # rndr_str = render_to_string("_sub_message_list.html" , {
    #                 'messages': messages,
    #                 'flag' : flag
    #                 }, request=request)
    return HttpResponse(rndr_str)

def turn_status(request):
    client_id = request.GET.get('client_id')
    status = request.GET.get('status')
    post_id = request.GET.get('post_id')
    client = Customer.objects.get(id=client_id)
    post = Post.objects.get(id=post_id)
    messages = Message.objects.filter(Q(customer_to=client, customer_from=request.user, post=post) | Q(customer_from=client, customer_to=request.user, post=post))
    for message in messages:
        if status == 'starred':
            message.starred = not message.starred
        if status == 'archieve':
            message.archieve = not message.archieve
        else:
            message.status = status
        message.save()
    return HttpResponse('')


def view_campaign(request, camp_id):
    campaign = Campaign.objects.get(id=camp_id)
    perks = Perk.objects.filter(campaign=campaign)
    result = ''

    if request.method == 'POST':
        perk = request.POST.get('perk_id') or -1
        contact = request.POST.get('contact')
        amount = request.POST.get('amount')
        claimer = request.user if request.user.is_authenticated() else None
        card = request.POST.get('stripeToken')

        perk = Perk.objects.filter(id=perk).first()

        try:
            stripe_account_id = SocialAccount.objects.get(user__id=campaign.owner.id, provider='stripe').uid

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=card, # obtained with Stripe.js
                destination=stripe_account_id,
                application_fee = int(amount * settings.APP_FEE),
                description="Contribute to the Campaign (#{} - {})".format(campaign.id, campaign.title)
            )

            PerkClaim.objects.create(campaign_id=camp_id,
                                     perk=perk,
                                     contact=contact,
                                     claimer=claimer,
                                     amount=amount,
                                     transaction=charge.id)
            # send notification email to the owner
            if perk:
                subject = 'Perk Claimatoin from Globalboard'
                content = "Perk ({}) in the campaign ({}) is claimed<br><br>Contact Info:<br>" \
                          .format(perk.title, campaign.title)

                # update perk's claimed count, used for cache for less db transaction
                perk.num_claimed = perk.num_claimed + 1
                perk.save()
            else:
                subject = 'Donation to your campaign on Globalboard'
                content = "Donation (${}) is made to the campaign ({})<br><br>Contact Info:<br>" \
                          .format(int(amount)/100, campaign.title)

            content += contact
            send_email(settings.FROM_EMAIL, subject, campaign.owner.email, content)

            # update campaign's raised amount, used for cache for less db transaction
            campaign.raised = campaign.raised + int(amount) / 100
            campaign.save()

            result = charge.id
        except Exception, e:
            print e, 'stripe error ##'
            # result = 'failed'


    return render(request, 'camp_detail.html', {
        'post': campaign,
        'perks': perks,
        'skey': settings.STRIPE_KEYS['PUBLIC_KEY'],
        'result': result
    })

def category_ads(request, category_id):
    # store category
    request.session['category'] = category_id
    request.session.modified = True

    category = Category.objects.get(id=category_id)

    tpl_map = {
        10: 'choose_dealer_class.html',
        30: 'disclaimer.html'
    }

    if category.column in tpl_map:
        return render(request, tpl_map[category.column], {'category': category})
    return category_ads_dealer(request, category_id, 'all')

def category_ads_dealer(request, category_id, kind):
    region_id = request.session.get('region')  # city
    if not region_id:
        return HttpResponseRedirect('/profile')
    region = City.objects.get(id=region_id)

    category = Category.objects.get(id=category_id)
    form = get_class(category.form+'Form')
    posts = Post.objects.filter(Q(region=region) | Q(region__district=region) | Q(region__isnull=True)) \
                        .filter(category_id=category_id).exclude(status='deactive') \
                        .order_by('-created_at')
    if kind == 'owner':
        posts = posts.filter(by_dealer=False)
    elif kind == 'dealer':
        posts = posts.filter(by_dealer=True)

    posts = get_posts_with_image(posts)
    breadcrumb_ = '<a class="breadcrumb-item" href="javascript:void();" data-mapname="custom/world">worldwide</a>'
    breadcrumb_ = retrieve_session(request, 'breadcrumb', breadcrumb_)

    return render(request, 'ads-list.html', {
        'posts': posts,
        'region': region,
        'category': category,
        'others': True,
        'breadcrumb': breadcrumb_,
        'skey': settings.STRIPE_KEYS['PUBLIC_KEY']
    })

@csrf_exempt
def send_friend_email(request):
    from_email = request.POST.get('from_email')
    to_email = request.POST.get('to_email')
    ads_id = request.POST.get('ads_id')
    post = Post.objects.get(id=ads_id)
    content = """
        {1} forwarded you this from Global Board:<br><br>
        <h3>{2}</h3><br><br>
        {0}/ads/{3}
        """.format(settings.MAIN_URL, from_email, post.title, post.id)

    send_email(settings.FROM_EMAIL, post.title, to_email, content)
    return HttpResponse('')

def region_ads(request, region_id, region):
    is_world = False
    if region == 'city':
        posts = Post.objects.filter(Q(region_id=region_id) | Q(region__district__id=region_id) | Q(region__isnull=True))
    elif region == 'state':
        posts = Post.objects.filter(Q(region__state__id=region_id) | Q(region__isnull=True))
    elif region == 'world':
        is_world = True
        posts = Post.objects.all()
    posts = get_posts_with_image(posts.exclude(status='deactive').order_by('-created_at'))
    breadcrumb_ = '<a class="breadcrumb-item" href="javascript:void();" data-mapname="custom/world">worldwide</a>'
    breadcrumb_ = retrieve_session(request, 'breadcrumb', breadcrumb_)
    return render(request, 'ads-list.html', {
        'posts': posts,
        'region': region_id,
        'others': True,
        'is_world': is_world,
        'category_list' : Category.objects.filter(parent=None),
        'breadcrumb': breadcrumb_
    })

def place_country_list(request):
    country_all_list = Country.objects.all()
    request.session['timeoffset'] = request.GET.get('timeoffset')
    try:
        country_code = request.GET.get('countryCode')
        state = request.GET.get('state')
        city = request.GET.get('city')
        state_abbr = request.GET.get('stateCode').lower()
        if country_code == "GB" and city == '' and state == '':
            city = 'London'
            state = 'England'
        default_site = ''
        try:
            country_list = Country.objects.filter(sortname__icontains=country_code)
            country_id = 0
            if len(country_list) > 0:
                country_id = country_list[0].id
            state_list = State.objects.filter(country=country_id)
            state_code = 0
            state_name = state
            state_instance = None
            for st in state_list:
                if SequenceMatcher(None, st.name, state).ratio() > 0.7:
                    state_code = st.id
                    state_name = st.name
                    state_instance = st
            city_list = City.objects.filter(state=state_code, name__icontains=city)
            city_code = ''
            if len(city_list) > 0:
                city_code += '@' + str(city_list[0].id)
            else:
                # city_list = City.objects.filter(state=state_code)
                # if len(city_list) > 0:
                #     city_code += '@' + str(city_list[0].id)
                add_city = City.objects.create(name=city, state=state_instance)
                city_code = add_city.id
                print('~~~~~~~~~~~ new city added : ', city, ' in ', state_name)
            if country_code.lower() in 'us ca':
                default_site = 'countries/'+country_code.lower()+'/'+country_code.lower()+'-'+state_abbr+'-all@'+state_name+city_code
            else:
                default_site = 'countries/'+country_code.lower()+'/'+country_code.lower()+'-all@'+state_name+city_code
            if request.user.is_authenticated():
                request.user.default_site = default_site
                request.user.save()
        except Exception as e:
            print('############', e)
            default_site = 'countries/'+country_code.lower()+'/'+country_code.lower()+'-all'

        request.session['default_site'] = default_site
        ret_arr = []
        # for country in country_all_list:
        #     if country.sortname != country_code:
        #         ret_arr.append({
        #             'name' : country.name,
        #             'sortname' : country.sortname
        #         })
    except:
        default_site = ''
    rndr_str = render_to_string('_country_list.html', {
        'css_class': '',
        'countries': country_all_list,
        'current_location':default_site
    })
    return HttpResponse(rndr_str)

# def globoard_display_world_countries():
#     country_list = Country.objects.all()
#     # default_country = {
#     #     'sortname': country_code,
#     #     'name': country
#     # }
#     # ret_arr = []
#     # ret_arr.append(default_country)
#     # for country in country_list:
#     #     if country.sortname != default_country['sortname']:
#     #         ret_arr.append({
#     #             'name' : country.name,
#     #             'sortname' : country.sortname
#     #         })
#     rndr_str = render_to_string('_country_list.html', {
#         'css_class': '',
#         'countries': country_list
#     })
#     return rndr_str

@csrf_exempt
def toggle_favourite(request):
    ads_id = request.POST.get('ads_id')
    res = 'success'
    if request.user.is_authenticated():
        if Favourite.objects.filter(owner=request.user, post_id=ads_id):
            Favourite.objects.filter(owner=request.user, post_id=ads_id).delete()
        else:
            Favourite.objects.create(owner=request.user, post_id=ads_id)
    else:
        res = 'fail'

    return HttpResponse(res)

@login_required(login_url='/accounts/login/')
def my_favourites(request):
    posts = [ii.post for ii in Favourite.objects.filter(owner=request.user)]
    posts = get_posts_with_image(posts)
    return render(request, 'ads-list.html', { 'posts': posts,
                                              'others': True,
                                              'no_subscription': True})

@login_required(login_url='/accounts/login/')
def my_subscriptions(request):
    searches = Search.objects.filter(owner=request.user)

    return render(request, 'my-subscription.html', {
        'searches': searches
    })

@login_required(login_url='/accounts/login/')
def edit_subscription(request, ss_id):
    categories = []
    states = []
    cities = []

    subscription = Search.objects.get(id=ss_id)
    if subscription.category:
        categories = subscription.category.parent.category_set.all()
    if subscription.state:
        states = subscription.state.country.state_set.all()
    if subscription.city:
        cities = subscription.city.state.city_set.all()

    if request.method == 'GET':
        form = SearchForm(instance=subscription)
    else:
        form = SearchForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()

            # charge for update
            # card = request.POST.get('stripeToken')
            # try:
            #     stripe.Charge.create(
            #         amount=50,
            #         currency="usd",
            #         source=card, # obtained with Stripe.js
            #         description="Charge for subscription({}) update".format(subscription.keyword)
            #     )
            # except Exception, e:
            #     print e, 'stripe error ##'

            return HttpResponseRedirect(reverse('my-subscriptions'))

    return render(request, 'subscription-edit.html', {
        'form': form,
        'categories': categories,
        'states': states,
        'cities': cities,
        'skey': settings.STRIPE_KEYS['PUBLIC_KEY'],
    })

@csrf_exempt
def create_subscription(request):
    keyword = request.POST.get('keyword')
    category = request.session['category']
    region_kind = request.session['region_kind']
    region_id = request.session['region']

    if region_kind == 'state':
        Search.objects.create(**{
            'owner': request.user,
            'keyword': keyword,
            'category_id': category,
            'state_id': region_id,
            'search_title': request.POST.get('search_title') == 'true',
            'has_image': request.POST.get('has_image') == 'true',
            'min_price': request.POST.get('min_price') or None,
            'max_price': request.POST.get('max_price') or None
        })
    else:
        Search.objects.create(**{
            'owner': request.user,
            'keyword': keyword,
            'category_id': category,
            'city_id': region_id,
            'search_title': request.POST.get('search_title') == 'true',
            'has_image': request.POST.get('has_image') == 'true',
            'min_price': request.POST.get('min_price') or None,
            'max_price': request.POST.get('max_price') or None
        })

    # charge for create
    card = request.POST.get('stripeToken')
    try:
        stripe.Charge.create(
            amount=200,
            currency="usd",
            source=card, # obtained with Stripe.js
            description="Charge for creation of new subscription({})".format(keyword)
        )
    except Exception, e:
        print e, 'stripe error ##'

    return HttpResponse('')

@csrf_exempt
def remove_subscription(request):
    sub_id = request.POST.get('sub_id')

    Search.objects.filter(id=sub_id).delete()
    return HttpResponse('')

@login_required(login_url='/accounts/login/')
def my_account(request):

    #  just for updating status of pending transactions, shuuld be updated with cronjob later

    try:

        bitcoin_transactions = client.get_transactions(settings.BITCOIN_ACCOUNT).data

        for trans in bitcoin_transactions:

            if trans.status == "completed":

                pur = PostPurchase.objects.filter(transaction=trans.network['hash'])

                if len(pur) > 0:

                    if pur[0].status != 0:

                        pur[0].status = 0

                        pur[0].save()
    except:
        pass


    tab = request.GET.get('tab', 'profile')
    purchase = request.GET.get('purchase')
    res_temp = []
    total_received_amount = 0

    rpurchases = PostPurchase.objects.all().order_by('-udpated_at')

    get_paid = request.user.get_paid

    wallet = 0.0

    #recevied purchases

    # finished purchases
    dpurchases = PostPurchase.objects.filter(purchaser=request.user, status=0) \
                                     .order_by('-udpated_at')
    # escrow purchases
    ppurchases = PostPurchase.objects.filter(purchaser=request.user).exclude(status=0) \
                                     .order_by('-created_at')

    categories = Review.objects.filter(post__owner=request.user) \
                               .values('post__category__name', 'post__category__parent__name',
                                       'post__category__id') \
                               .distinct()


    rpurchases_list = [] #  received payments

    for rpur in rpurchases:

        if rpur.post.owner.id == request.user.id:

            if rpur.type == 'direct':

                if rpur.status == 0:

                    rpurchases_list.append({
                        "id": rpur.id,
                        "transaction" : rpur.transaction,
                        "post_id" : rpur.post.id,
                        "post_title" : rpur.post.title,
                        "post_price" : rpur.post.price,
                        "received_amount" : rpur.post.price * (1.0 - settings.APP_FEE),
                        "date" : rpur.udpated_at,
                        "type" : rpur.type,
                        "service_fee" : rpur.post.price * settings.APP_FEE,
                        "category" : rpur.post.category.parent.name if rpur.post.category.parent.name !='' else rpur.post.category.name
                    })

                    wallet += rpur.post.price
            else :

                if rpur.paid_percent != 0:

                    rpurchases_list.append({
                        "id": rpur.id,
                        "transaction" : rpur.transaction,
                        "post_id" : rpur.post.id,
                        "post_title" : rpur.post.title,
                        "post_price" : rpur.post.price,
                        "received_amount" : (float(rpur.paid_percent)/100.0) * rpur.post.price * (1.0 - settings.APP_FEE),
                        "date" : rpur.udpated_at,
                        "type" : rpur.type,
                        "service_fee" : (float(rpur.paid_percent)/100.0) * rpur.post.price * settings.APP_FEE,
                        "category" : rpur.post.category.parent.name  if rpur.post.category.parent.name !='' else rpur.post.category.name
                    })

                wallet += (float(rpur.paid_percent)/100.0) * rpur.post.price * (1.0 - settings.APP_FEE)

    ppurchases_list = [] #  pending payments


    for ppur in ppurchases:

        p_m = ''

        if 'ch_' in ppur.transaction.lower():

            p_m = 'Stripe'

        elif 'payid-' in ppur.transaction.lower():

            p_m = 'Paypal'

        else:

            p_m = 'Bitcoin'

        ppurchases_list.append({
            "id": ppur.id,
            "transaction" : ppur.transaction,
            "post_id" : ppur.post.id,
            "post_title" : ppur.post.title,
            "post_price" : ppur.post.price,
            "paid_percent" : ppur.paid_percent,
            "approved" : (float(ppur.paid_percent)/100.0) * ppur.post.price if ppur.paid_percent > 0 else 0,
            "date" : ppur.created_at,
            "service_fee" : settings.APP_FEE * 100,
            "status" : "Review" if ppur.status == 3 else "Available",
            "payment_method" : p_m
        })

        # wallet += (float(ppur.paid_percent)/100.0) * ppur.post.price if ppur.paid_percent > 0 else 0

    dpurchases_list = []    #  finished payments

    cpurchases_list = []    #  canceled payments

    for dpur in dpurchases:

        if dpur.type == 'direct' or dpur.paid_percent == 100:

            dpurchases_list.append({
                "id": dpur.id,
                "transaction" : dpur.transaction,
                "post_id" : dpur.post.id,
                "post_title" : dpur.post.title,
                "post_price" : dpur.post.price,
                "paid_percent" : dpur.paid_percent,
                "type" : dpur.type,
                "approved" : (float(dpur.paid_percent)/100.0) * dpur.post.price * (1.0 - settings.APP_FEE) if dpur.paid_percent > 0 else 0,
                "date" : dpur.created_at,
                "service_fee" : settings.APP_FEE_BUY * dpur.post.price,
                "total_amount" : (settings.APP_FEE_BUY +1 ) * dpur.post.price,
                "category" : dpur.post.category.parent.name if dpur.post.category.parent.name !='' else dpur.post.category.name
            })

        else :
            cpurchases_list.append({
                "id": dpur.id,
                "transaction" : dpur.transaction,
                "post_id" : dpur.post.id,
                "post_title" : dpur.post.title,
                "post_price" : dpur.post.price,
                "paid_percent" : dpur.paid_percent,
                "type" : dpur.type,
                "paid_amount" : dpur.post.price * float(dpur.paid_percent/100.0),
                "approved" : dpur.post.price * float(dpur.paid_percent/100.0) * (1.0 + settings.APP_FEE_BUY),
                "date" : dpur.udpated_at,
                "service_fee" : settings.APP_FEE_BUY * dpur.post.price * float(dpur.paid_percent/100.0),
                "total_service_fee" : settings.APP_FEE_BUY * dpur.post.price,
                "refund_amount" : dpur.post.price * float((100 - dpur.paid_percent)/100.0),
                "total_amount" : (settings.APP_FEE_BUY +1 ) * dpur.post.price,
                "category" : dpur.post.category.parent.name if dpur.post.category.parent.name !='' else dpur.post.category.name,

                # Added new data
                "total_price": dpur.post.price,
                "received_amount": dpur.post.price * settings.APP_FEE,
                "received_percentage": dpur.post.price * dpur.paid_percent / 100.0,
                "cancelled_amount": dpur.post.price * (1.0 - (dpur.paid_percent / 100.0)),
                "service_fees": dpur.post.price * (1.0 - (dpur.paid_percent / 100.0)),
                "total_amount_received": dpur.post.price * (dpur.paid_percent / 100.0 - settings.APP_FEE) if dpur.paid_percent != 0 else 0,
            })


    for ii in categories:
        ii['reviews'] = Review.objects.filter(post__owner=request.user,
                                              post__category__id=ii['post__category__id'])


    if request.method == 'GET':
        form = CustomerForm(instance=request.user)
    else:
        form = CustomerForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

    wallet = wallet - get_paid

    return render(request, 'my-account.html', {
        'host': request.user,
        'form': form,
        'tab': tab,
        'reviews': categories,
        'dpurchases': dpurchases_list,
        'ppurchases': ppurchases_list,
        'cpurchases': cpurchases_list,
        'rpurchases' : rpurchases_list,
        'num_reviews': Review.objects.filter(post__owner=request.user).count(),
        'stripe': request.user.socialaccount_set.filter(provider='stripe'),
        'total_received_amount' : total_received_amount,
        'APP_FEE' : settings.APP_FEE,
        'APP_FEE_BUY' : settings.APP_FEE_BUY,
        'category_list' : Category.objects.filter(parent=None),
        'wallet' : wallet,
        'paypal_client': settings.PAYPAL_CLIENT,
        'skey': settings.STRIPE_KEYS['PUBLIC_KEY']
    })




def search_txs(request):
    tx_type = request.GET.get('tx_type')
    keyword = request.GET.get('tx_key')
    payment_method = request.GET.get('tx_payment_method')
    category = request.GET.get('tx_category')
    start_date = request.GET.get('tx_start_date')
    end_date = request.GET.get('tx_end_date')

    if start_date == '':
        start_date = '1900-01-01'

    if end_date == '':
        end_date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    if tx_type == "pending":

        ppurchases_list = []

        ppurchases = PostPurchase.objects.filter(purchaser=request.user, created_at__range=[start_date, end_date]).exclude(status=0) \
                                         .order_by('-created_at')


        for ppur in ppurchases:

            if (category in ppur.post.category.name or category in ppur.post.category.parent.name):

                if ( keyword != None and keyword.lower() in ppur.post.title.lower()) or keyword == None  :

                    check = False

                    if payment_method == 'bc_':

                        if 'payid-' not in ppur.transaction.lower() and 'ch_' not in ppur.transaction.lower():

                            check = True

                    else:

                        if payment_method in ppur.transaction.lower():

                            check = True

                    if check :

                        p_m = ''

                        if 'ch_' in ppur.transaction.lower():

                            p_m = 'Stripe'

                        elif 'payid-' in ppur.transaction.lower():

                            p_m = 'Paypal'

                        else:

                            p_m = 'Bitcoin'

                        ppurchases_list.append({
                                "id": ppur.id,
                                "transaction" : ppur.transaction,
                                "post_id" : ppur.post.id,
                                "post_title" : ppur.post.title,
                                "post_price" : ppur.post.price,
                                "paid_percent" : ppur.paid_percent,
                                "approved" : (float(ppur.paid_percent)/100) * ppur.post.price if ppur.paid_percent > 0 else 0,
                                "date" : ppur.created_at,
                                "service_fee" : settings.APP_FEE * 100,
                                "status" : "Review" if ppur.status == 3 else "Available",
                                "payment_method" : p_m
                            })

        rndr_str = render_to_string("_transactions_pending.html" , {
                    'ppurchases': ppurchases_list,
                    'APP_FEE' : settings.APP_FEE,
                    'APP_FEE_BUY' : settings.APP_FEE_BUY
                    }, request=request)

        return HttpResponse(rndr_str)

    if tx_type == "finished":

        dpurchases_list = []

        dpurchases = PostPurchase.objects.filter(purchaser=request.user, status=0, created_at__range=[start_date, end_date]) \
                                     .order_by('-created_at')

        for dpur in dpurchases:


            if (category in dpur.post.category.name or category in dpur.post.category.parent.name):

                if dpur.type == 'direct' or dpur.paid_percent == 100:

                    if ( keyword != None and keyword.lower() in dpur.post.title.lower()) or keyword == None  :

                        check = False

                        if payment_method == 'bc_':

                            if 'payid-' not in dpur.transaction.lower() and 'ch_' not in dpur.transaction.lower():

                                check = True

                        else:

                            if payment_method in dpur.transaction.lower():

                                check = True

                        if check:

                            dpurchases_list.append({
                                    "id": dpur.id,
                                    "transaction" : dpur.transaction,
                                    "post_id" : dpur.post.id,
                                    "post_title" : dpur.post.title,
                                    "post_price" : dpur.post.price,
                                    "paid_percent" : dpur.paid_percent,
                                    "type" : dpur.type,
                                    "approved" : (float(dpur.paid_percent)/100) * dpur.post.price * (1.0 - settings.APP_FEE) if dpur.paid_percent > 0 else 0,
                                    "date" : dpur.created_at,
                                    "service_fee" : settings.APP_FEE_BUY * dpur.post.price,
                                    "total_amount" : (settings.APP_FEE_BUY +1 ) * dpur.post.price,
                                    "category" : dpur.post.category.parent.name if dpur.post.category.parent.name !='' else dpur.post.category.name
                                })


        rndr_str = render_to_string("_transactions_finished.html" , {'dpurchases': dpurchases_list}, request=request)

        return HttpResponse(rndr_str)


    if tx_type == "cancelled":

        cpurchases_list = []

        cpurchases = PostPurchase.objects.filter(purchaser=request.user, status=0, udpated_at__range=[start_date, end_date]) \
                                     .order_by('-udpated_at')

        for cpur in cpurchases:

            if (category in cpur.post.category.name or category in cpur.post.category.parent.name):

                if cpur.paid_percent != 100:

                    if ( keyword != None and keyword.lower() in cpur.post.title.lower()) or keyword == None  :

                        check = False

                        if payment_method == 'bc_':

                            if 'payid-' not in cpur.transaction.lower() and 'ch_' not in cpur.transaction.lower():

                                check =True

                        else:

                            if payment_method in cpur.transaction.lower():

                                check =True

                        if check:

                            cpurchases_list.append({
                                   "id": cpur.id,
                                    "transaction" : cpur.transaction,
                                    "post_id" : cpur.post.id,
                                    "post_title" : cpur.post.title,
                                    "post_price" : cpur.post.price,
                                    "paid_percent" : cpur.paid_percent,
                                    "type" : cpur.type,
                                    "paid_amount" : cpur.post.price * float(cpur.paid_percent/100.0),
                                    "approved" : cpur.post.price * float(cpur.paid_percent/100.0) * (1.0 + settings.APP_FEE_BUY),
                                    "date" : cpur.udpated_at,
                                    "service_fee" : settings.APP_FEE_BUY * cpur.post.price * float(cpur.paid_percent/100.0),
                                    "total_service_fee" : settings.APP_FEE_BUY * cpur.post.price,
                                    "refund_amount" : cpur.post.price * float((100 - cpur.paid_percent)/100.0),
                                    "total_amount" : (settings.APP_FEE_BUY +1 ) * cpur.post.price,
                                    "category" : cpur.post.category.parent.name if cpur.post.category.parent.name !='' else cpur.post.category.name
                                })

        rndr_str = render_to_string("_transactions_cancelled.html" , {'cpurchases': cpurchases_list}, request=request)

        return HttpResponse(rndr_str)


    if tx_type == "received":

        rpurchases_list = []

        rpurchases = PostPurchase.objects.filter(udpated_at__range=[start_date, end_date]).order_by('-udpated_at')

        for rpur in rpurchases:

            if (category in rpur.post.category.name or category in rpur.post.category.parent.name):

                check = False

                if payment_method == 'bc_':

                    if 'payid-' not in rpur.transaction.lower() and 'ch_' not in rpur.transaction.lower():

                        check = True

                else:

                    if payment_method in rpur.transaction.lower():

                        check = True


                if check and (( keyword != None and keyword.lower() in rpur.post.title.lower()) or keyword == None):

                    if rpur.post.owner.id == request.user.id:

                        if rpur.type == 'direct':

                            if rpur.status == 0:

                                rpurchases_list.append({
                                    "id": rpur.id,
                                    "transaction" : rpur.transaction,
                                    "post_id" : rpur.post.id,
                                    "post_title" : rpur.post.title,
                                    "post_price" : rpur.post.price,
                                    "received_amount" : rpur.post.price * (1.0 - settings.APP_FEE),
                                    "date" : rpur.udpated_at,
                                    "type" : rpur.type,
                                    "service_fee" : rpur.post.price * settings.APP_FEE,
                                    "category" : rpur.post.category.parent.name if rpur.post.category.parent.name !='' else rpur.post.category.name
                                })
                        else :

                            if rpur.paid_percent != 0:

                                rpurchases_list.append({
                                    "id": rpur.id,
                                    "post_id" : rpur.post.id,
                                    "transaction" : rpur.transaction,
                                    "post_title" : rpur.post.title,
                                    "post_price" : rpur.post.price,
                                    "received_amount" : (float(rpur.paid_percent)/100) * rpur.post.price * (1.0 - settings.APP_FEE),
                                    "date" : rpur.udpated_at,
                                    "type" : rpur.type,
                                    "service_fee" : (float(rpur.paid_percent)/100) * rpur.post.price * settings.APP_FEE,
                                    "category" : rpur.post.category.parent.name  if rpur.post.category.parent.name !='' else rpur.post.category.name
                                })

        rndr_str = render_to_string("_transactions_received.html" , {'rpurchases': rpurchases_list}, request=request)

        return HttpResponse(rndr_str)

@csrf_exempt
def send_vcode(request):
    phone = request.POST.get('phone')
    vcode = randint(100000, 999999)
    print vcode, '###'
    body = "{} is your Globalboard verification code.".format(vcode)
    result = send_SMS(phone, body)

    if result:
        request.session['vcode'] = str(vcode)
        request.session['phone'] = phone
        request.session.modified = True
        return HttpResponse('success')
    else:
        return HttpResponse('fail')

@csrf_exempt
def verify_phone(request):
    code = request.POST.get('vcode')
    vcode = request.session['vcode']

    if code == vcode:
        request.user.phone_verified = True
        request.user.phone = request.session['phone']
        request.user.save()
        return HttpResponse('success')
    else:
        return HttpResponse('fail')

@csrf_exempt
def upload_id(request):
    id_photo = request.POST.get('id_photo')
    request.user.v_statue = 'awaiting_approve'
    # send an email to administrator
    content = """user {1} uploaded his ID.<br> Please check and approve it
                 <a href="{0}/admin/general/customer/{2}/change/">here</a>.
    """.format(settings.MAIN_URL, request.user.username, request.user.id)

    send_email(settings.FROM_EMAIL, 'Verification Submitted', settings.ADMIN_EMAIL, content)
    request.user.id_photo = 'ID/' + id_photo
    request.user.save()
    return HttpResponse('')

def confirm_phone(request):
    return render(request, 'account/phone_confirm.html')

@login_required(login_url='/accounts/login/')
def my_campaigns(request):
    campaigns_ = []
    campaigns = Campaign.objects.filter(owner=request.user).order_by('-created_at')

    for ii in campaigns:
        if ii.created_at >= datetime.datetime.now().date() + datetime.timedelta(days=-ii.duration):
            campaigns_.append(ii)

    return render(request, 'my-campaigns.html', {
        'campaigns': campaigns,
        'mine': True
    })

@login_required(login_url='/accounts/login/')
def post_camp(request, camp_id):
    categories = CampCategory.objects.all()
    stripe_connected = SocialAccount.objects.filter(user=request.user, provider='stripe').exists()
    if request.method == 'GET':
        form = CampaignForm()
    else:
        form = CampaignForm(request.POST, request.FILES)

        if form.is_valid():
            camp = form.save()
            num_perks = int(request.POST.get('num_perks'))
            fs = FileSystemStorage()

            iii = 0
            for ii in range(num_perks):
                filename = None
                if request.POST.getlist('flag_perk_overview')[ii]:
                    perk_img = request.FILES.getlist('perk_overview')[iii]
                    filename = fs.save('perks/'+perk_img.name, perk_img)
                    iii += 1

                Perk.objects.create(title=request.POST.getlist('perk_title')[ii],
                                    campaign=camp,
                                    price=request.POST.getlist('perk_price')[ii],
                                    description=request.POST.getlist('perk_desc')[ii],
                                    num_avail=request.POST.getlist('perk_avail_num')[ii] or 1000000,
                                    image=filename)

            return HttpResponseRedirect(reverse('my-campaigns'))
        print(form.errors, '$$$$$$$$')
    return render(request, 'post_camp.html', {
        'form': form,
        'categories': categories,
        'stripe_connected': stripe_connected,
        'rng_perks': range(1, 11)
    })

def explorer_campaigns(request):
    categories = CampCategory.objects.all()
    campaigns = Campaign.objects.all().order_by('-created_at')
    for campaign in campaigns:
        if 'campaigns' not in campaign.over_image:
            campaign.over_image = 'campaigns/' + campaign.over_image
    return render(request, 'campaign-list.html', {
        'categories': categories,
        'campaigns': campaigns
    })

@csrf_exempt
def search_camps(request):
    keyword = request.POST.get('keyword')
    category = request.POST.get('category')
    others = request.POST.get('others')

    # if others:
        # .filter(owner=request.user)
    campaigns = Campaign.objects.filter(Q(title__icontains=keyword)
                                      | Q(overview__icontains=keyword)
                                      | Q(tagline__icontains=keyword))
    if category:
        campaigns = campaigns.filter(Q(category=category) | Q(category__parent=category))

    campaigns_ = []
    for ii in campaigns:
        if ii.created_at >= datetime.datetime.now().date() + datetime.timedelta(days=-ii.duration):
            campaigns_.append(ii)

    rndr_str = render_to_string('_camp_list.html', {'campaigns': campaigns_})
    return HttpResponse(rndr_str)

@csrf_exempt
def rate_ads(request):

    Review.objects.create(post_id=request.POST.get('post_id'),
                          rater=request.user,
                          purchase_id=request.POST.get('purchase_id'),
                          rating=request.POST.get('rating'),
                          content=request.POST.get('content'))

    return HttpResponse('')

def user_show(request, user_id):
    host = Customer.objects.get(id=user_id)
    categories = Review.objects.filter(post__owner=host) \
                               .values('post__category__name', 'post__category__parent__name',
                                       'post__category__id') \
                               .distinct()
    for ii in categories:
        ii['reviews'] = Review.objects.filter(post__owner=host,
                                              post__category__id=ii['post__category__id'])

    return render(request, 'user_show.html', {
        'host': host,
        'reviews': categories,
        'num_reviews': Review.objects.filter(post__owner=host).count()
    })

@csrf_exempt
def release_purchase(request):

    message = ""

    p_id = request.POST.get('p_id')
    percent = int(request.POST.get('percent'))


    purchase = PostPurchase.objects.get(id=p_id)

    # send money to the post's owner
    amount = int(purchase.post.price * percent )

    purchase.paid_percent = purchase.paid_percent + percent

    if purchase.paid_percent == 100:    # finished purchase
        purchase.status = 0

    purchase.save()

    result = {
        # "transaction": transfer.id,
        "finished": purchase.paid_percent == 100,
        "message" : message
    }

    return JsonResponse(result, safe=False)

    # if 'payid-' in purchase.transaction.lower():

    #     amount = purchase.post.price * percent/100

    #     receiver_email = purchase.post.owner.paypal

    #     payout = paypalrestsdk.Payout({
    #         "sender_batch_header": {
    #             "sender_batch_id": "batch",
    #             "email_subject": "You have a payment"
    #         },
    #         "items": [
    #             {
    #                 "recipient_type": "EMAIL",
    #                 "amount": {
    #                     "value": amount,
    #                     "currency": "USD"
    #                 },
    #                 "receiver": receiver_email,
    #                 "note": "Thank you.",
    #                 "sender_item_id": "item"
    #             }
    #         ]
    #     })

    #     if payout.create(sync_mode=False):
    #         print("payout[%s] created successfully" %
    #           (payout.batch_header.payout_batch_id))

    #         purchase.paid_percent = purchase.paid_percent + percent
    #         if purchase.paid_percent == 100:    # finished purchase
    #             purchase.status = 0

    #         purchase.save()

    #         result = {
    #             "transaction": transfer.id,
    #             "finished": purchase.paid_percent == 100,
    #             "message" : message
    #         }

    #         return JsonResponse(result, safe=False)

    #     else:
    #         print(payout.error)

    # else:

    #     destination = ''

    #     try:

    #         destination=purchase.post.owner.socialaccount_set.get(provider='stripe').uid

    #         try:

    #             transfer = stripe.Transfer.create(
    #                 amount=amount,
    #                 currency="usd",
    #                 source_transaction=purchase.transaction,
    #                 destination=destination
    #             )

    #             purchase.transaction = transfer.id

    #             purchase.paid_percent = purchase.paid_percent + percent
    #             if purchase.paid_percent == 100:    # finished purchase
    #                 purchase.status = 0

    #             purchase.save()

    #             result = {
    #                 "transaction": transfer.id,
    #                 "finished": purchase.paid_percent == 100,
    #                 "message" : message
    #             }

    #             return JsonResponse(result, safe=False)

    #         except Exception as e:

    #             print(e, "~~~~~~~~~here")

    #             return JsonResponse({"message" : "Something went wrong. Please contact with the Administrator."}, safe=False)

    #     except:

    #         message = "The payment can't be processed because the customer doesn't connect with his stripe account."

    #         return JsonResponse({"message" : message}, safe=False)


@csrf_exempt
def cancel_purchase(request):

    post_id = request.POST.get('p_id')

    purchase_id = request.POST.get('purchase_id')

    purchase = PostPurchase.objects.get(id=purchase_id)

    if 'ch_' in purchase.transaction :

        destination=purchase.purchaser.socialaccount_set.get(provider='stripe').uid

        amount = int((100 - purchase.paid_percent ) * purchase.post.price)

        try:

            destination=purchase.post.owner.socialaccount_set.get(provider='stripe').uid

            transfer = stripe.Transfer.create(
                amount=amount,
                currency="usd",
                source_transaction=purchase.transaction,
                destination=destination
            )

            purchase.status = 0

            purchase.save()


        except Exception as e:

            print(e, "~~~~~~~~~")

    if 'payid-' in purchase.transaction.lower():

        receiver_email = paypalrestsdk.Payment.find(purchase.transaction).payer.payer_info.email

        amount = math.ceil((1 - purchase.paid_percent/100)*purchase.post.price*100)/100

        payout = paypalrestsdk.Payout({
            "sender_batch_header": {
                "sender_batch_id": "refund-"+purchase.transaction,
                "email_subject": "You have a payment"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": amount,
                        "currency": "USD"
                    },
                    "receiver": receiver_email,
                    "note": "Fefunded",
                    "sender_item_id": "item"
                }
            ]
        })

        if payout.create(sync_mode=False):

            print('~~~~~~~~~~~~~~~~~~~~')
            print("refunded[%s] created successfully" %
                  (payout.batch_header.payout_batch_id))

            purchase.status = 0

            purchase.save()

        else:
            print('###############')
            print(payout.error)



        print('~~~~~~~~~~ paypal cancellation ~~~~~~~~~~~')

    return JsonResponse({"message" :"The tranasction is Cancelled successfully."}, safe=False)


@csrf_exempt
def withdraw_money(request):

    amount = int(float(request.POST.get('amount')))

    payment_method = request.POST.get('payment_method')

    res_message = "Withdrawn Successfully"

    if payment_method == "stripe":

        try:

            stripe_token = stripe.Token.create(
                settings.COMPANY_CARD,
            )

            stripe_account_id = SocialAccount.objects.get(user=request.user, provider='stripe').uid

            charge = stripe.Charge.create(
                    amount=amount * 100,
                    currency="usd",
                    source=stripe_token,
                    destination=stripe_account_id,
                    # application_fee = int(amount * settings.APP_FEE_BUY),
                    description="Direct pay to the ads"
                )

            get_paid = request.user.get_paid

            get_paid += amount

            request.user.get_paid = get_paid

            request.user.save()

        except:

            res_message = "You don't have enough ballence in your Stripe. Try again, please."


    elif payment_method == "bitcoin":

        try:

            address = request.POST.get('address')

            b = BtcConverter()

            cur = b.convert_to_btc_on(amount, 'USD', datetime.datetime.now() - datetime.timedelta(days=1))

            tx = client.send_money(settings.BITCOIN_ACCOUNT,
                           to=address,
                           amount=cur,
                           currency='BTC')

            get_paid = request.user.get_paid

            get_paid += amount

            request.user.get_paid = get_paid

            request.user.save()

        except Exception as e:

            res_message = "You don't have enough ballence in your Bitcoin wallet. Try again, please."

    else:

        try:

            status = 0

            receiver_email = request.POST.get('email')

            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": "withdraw-"+str(request.user.id)+"-"+str(datetime.datetime.now()),
                    "email_subject": "You have a payment"
                },
                "items": [
                    {
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": amount,
                            "currency": "USD"
                        },
                        "receiver": receiver_email,
                        "note": "Thank you.",
                        "sender_item_id": "item"
                    }
                ]
            })

            if payout.create(sync_mode=False):
                print("payout[%s] created successfully" %
                      (payout.batch_header.payout_batch_id))

                get_paid = request.user.get_paid

                get_paid += amount

                request.user.get_paid = get_paid

                request.user.save()
            else:
                print(payout.error)

                res_message = "You don't have enough ballence in your Paypal. Try again, please."

        except:

            res_message = "You don't have enough ballence in your Paypal. Try again, please."

    # return redirect('my-account')
    return JsonResponse({"message" : res_message}, safe=False)


def chat_send_email(request):
    from_email = request.GET.get('from_email')
    from_phone = request.GET.get('from_phone')
    content = request.GET.get('content')
    to_email = request.GET.get('to_email')
    to_phone = request.GET.get('to_phone')
    print(from_email, '~~~~~~~', content, '~~~~~~',to_email)
    if to_email and to_email != '':
        send_email(from_email, "globalboard.world", to_email, content)
    if to_email != '' and from_email != '':
        send_SMS_Chat(from_phone, to_phone, content)
    return HttpResponse('')


@csrf_exempt
def update_alert(request):
    sid = request.POST.get('sid')
    alert = request.POST.get('alert') == 'true'
    Search.objects.filter(id=sid).update(alert=alert)
    return HttpResponse('')

def multiply(value, arg):
    return value*arg

