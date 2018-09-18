import datetime

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kojoslist.settings")
django.setup()

from django.utils import timezone
from django.conf import settings

from general.models import *
from general.utils import send_email

def main():
    for post in Post.objects.all():
        if post.status == 'expired':
            continue
        if post.updated_at <= timezone.now() + datetime.timedelta(days=-post.category.duration):
            subject = 'Expired Ad'
            content = ' You Ad ( {} ) has expired. Click link to renew ad. https://www.kojoslist/post-ads/{}'.format(post.title, post.id)
            send_email(settings.FROM_EMAIL, subject, post.owner.email, content)
            post.status = 'expired'
            post.save()


if __name__ == "__main__":
    main()
