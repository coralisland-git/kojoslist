# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

class CSession(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    val = models.TextField(default="{}")

    def __str__(self):
        return self.key


VSTATUS = (
    ('unverified', 'Unverified'),
    ('awaiting_approve', 'Awaiting Approve'),
    ('approved', 'Approved')
)

SSTATUS = (
    ('read', 'Read'),
    ('starred', 'Starred'),
    ('unread', 'Unread'),
    ('reservations', 'Reservations'),
    ('pending_requests', 'Pending Requests'),
    ('archieve', 'Archieve')
)


class Customer(AbstractUser):
    avatar = models.CharField(max_length=100, default="default_avatar.png")
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    dob = models.CharField(max_length=50, blank=True, null=True)
    forum_handle = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    get_paid = models.IntegerField(default=0)
    # cache location
    default_site = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    v_statue = models.CharField(max_length=50, choices=VSTATUS, default='unverified')
    id_photo = models.ImageField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # wallet = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Category(models.Model):
    parent = models.ForeignKey("Category", blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    column = models.IntegerField(default=1) # 10: dealer for sub category
    form = models.CharField(max_length=50, default='Post')
    price = models.FloatField(default=0)
    order = models.IntegerField(default=1) # for display
    duration = models.IntegerField(default=30) # for display

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ads Category'
        verbose_name_plural = 'Ads Categories'
        ordering = ['name']


class Country(models.Model):
    sortname = models.CharField(max_length=3)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'


class State(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name.encode('utf-8')


class City(models.Model):
    """
    cities do not have district
    districts have district as parent city
    """
    name = models.CharField(max_length=30)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey("City", blank=True, null=True, related_name='districts', on_delete=models.CASCADE)

    def __str__(self):
        return self.name.encode('utf-8')

    class Meta:
        verbose_name_plural = 'Cities'


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.FloatField(default=0, blank=True, null=True)
    tag = models.CharField(max_length=100, null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    region = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    language = models.CharField(max_length=50, blank=True, null=True)
    # contact
    mail_relay = models.BooleanField(default=False)
    real_email = models.BooleanField(default=False)
    no_reply = models.BooleanField(default=False)
    by_phone = models.BooleanField(default=False)
    by_text = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    allow_other_contact = models.BooleanField(default=False)
    by_dealer = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    test = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


PURCHASE_TYPE = (
    ('direct', 'DIRECT'),
    ('escrow', 'ESCROW')
)

PURCHASE_STATUS = (
    (0, 'FINISHED SUCCESSFULLY'),
    (1, 'WAIT RELEASE'),
    (2, 'UNDER DISPUTE'),
    (3, 'UNDER REVIEW')
)

class PostPurchase(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    purchaser = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=PURCHASE_TYPE)
    contact = models.TextField(blank=True, null=True)
    transaction = models.CharField(max_length=100)
    status = models.IntegerField(choices=PURCHASE_STATUS, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    udpated_at = models.DateTimeField(auto_now=True)
    paid_percent = models.IntegerField(default=0)   # used in escrow mode (0-100)

    def __str__(self):
        return '{} - {}'.format(self.post.title, self.purchaser.username)


class Review(models.Model):
    """
    review on post
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rater = models.ForeignKey(Customer, on_delete=models.CASCADE)
    purchase = models.ForeignKey(PostPurchase, null=True, on_delete=models.CASCADE)
    rating = models.FloatField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} - {}'.format(self.post.title, self.rater.username)


class Search(models.Model):
    keyword = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    alert = models.BooleanField(default=True)
    search_title = models.BooleanField(default=False)
    has_image = models.BooleanField(default=False)
    min_price = models.FloatField(blank=True, null=True)
    max_price = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.owner.username

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'


class Image(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_head = models.BooleanField(default=False)
    
    def __str__(self):
        return '{} - {}'.format(self.post.title, self.name)

class Favourite(models.Model):
    owner =  models.ForeignKey(Customer, related_name="favourites", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.owner.first_name, self.post.title)


class Hidden(models.Model):
    owner =  models.ForeignKey(Customer, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='post', on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.owner.first_name, self.post.title)


class Perk(models.Model):
    title = models.CharField(max_length=200)
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE)
    price = models.IntegerField()
    retail = models.IntegerField(default=0)
    description = models.TextField()
    num_avail = models.IntegerField(default=1000000)
    num_claimed = models.IntegerField(default=0)
    image = models.ImageField(upload_to="perks", blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.campaign.title, self.title)


class PerkClaim(models.Model):
    campaign = models.ForeignKey("Campaign", related_name="claims", on_delete=models.CASCADE)
    # null for donate
    perk = models.ForeignKey(Perk, blank=True, null=True, related_name="claims", on_delete=models.CASCADE)
    contact = models.TextField(blank=True, null=True)
    # null for Anonymous
    claimer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.CASCADE)
    amount = models.IntegerField()      # in cent
    transaction = models.CharField(max_length=100)

    def __str__(self):
        return self.campaign.title


class CampCategory(models.Model):
    parent = models.ForeignKey("CampCategory", blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    column = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Campaign Category'
        verbose_name_plural = 'Campaign Categories'


STAGES = [
    ('concept', 'CONCEPT'),
    ('prototype', 'PROTOTYPE'),
    ('production', 'PRODUCTION'),
    ('shipping', 'SHIPPING')
]

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(CampCategory, on_delete=models.CASCADE)
    budget = models.IntegerField()
    raised = models.IntegerField(default=0)
    over_image = models.CharField(max_length=200)
    overview = models.TextField()
    content = models.TextField()
    stage = models.CharField(max_length=200, choices=STAGES)
    duration = models.IntegerField()
    tagline = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    # youtube video keys
    videos = models.TextField(blank=True, null=True)
    owner =  models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title 


class Message(models.Model):
    customer_from = models.ForeignKey(Customer, related_name='customer_from', null=True, on_delete=models.CASCADE)
    customer_to = models.ForeignKey(Customer, related_name='customer_to', null=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, on_delete=models.CASCADE  )
    content = models.CharField(max_length=500, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=SSTATUS, default="unread")
    starred = models.BooleanField(default=False)
    archieve = models.BooleanField(default=False)
