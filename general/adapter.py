import json
import time, random, hmac, urllib, httplib

from hashlib import sha1
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        default_site = request.user.default_site
        path = '/'
        if default_site:
            path = "/profile"
        return path

    def confirm_email(self, request, email_address):
        try:
            nonce = str(random.randint(1, 10000))
            timestamp = str(int(time.time()))

            application_id = settings.QB_APPLICATION_ID
            auth_key = settings.QB_AUTH_KEY
            auth_secret = settings.QB_AUTH_SECRET

            # 1. create session
            signature_raw_body = ("application_id=" + application_id + "&auth_key=" + auth_key + 
                        "&nonce=" + nonce + "&timestamp=" + timestamp)

            signature = hmac.new(auth_secret, signature_raw_body, sha1).hexdigest()

            params = urllib.urlencode({'application_id': application_id, 
                                       'auth_key': auth_key, 
                                       'timestamp': timestamp, 
                                       'nonce' : nonce,
                                       'signature' : signature})

            conn = httplib.HTTPSConnection("api.quickblox.com")
            conn.request("POST", "/session.json", params, {})
            response = conn.getresponse()       # get response of api call
            res = json.loads(response.read())   # parse response as json
            token = res['session']['token']
            print token

            # 2. signup
            users = { "user": 
                {  'email': email_address.email, 
                   'password': 'kojoslist@123',
                   'full_name': email_address.user.first_name + ' ' + email_address.user.last_name
                }
            }

            print users, '#####3'
            params = json.dumps(users)

            headers = {
                'Content-type': 'application/json',
                'QB-Token': token
            }

            conn.request("POST", "/users.json", params, headers)
            response = conn.getresponse()
            print response.read(), '##########3'

            return super(MyAccountAdapter, self).confirm_email(request, email_address)
        except Exception, e:
            print str(e), 'Error in confirm_email @@@@@@@@@@@@@@'

class MySocialAdapter(DefaultSocialAccountAdapter):
    
    def get_connect_redirect_url(self, request, socialaccount):
        return '/my-account'