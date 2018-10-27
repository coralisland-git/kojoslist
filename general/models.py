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

class Customer(AbstractUser):
    avatar = models.CharField(max_length=100, default="default_avatar.png")
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    dob = models.CharField(max_length=50, blank=True, null=True)
    forum_handle = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    paypal = models.CharField(max_length=200, blank=True, null=True)
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
    parent = models.ForeignKey("Category", blank=True, null=True)
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
    country = models.ForeignKey(Country)

    def __str__(self):
        return self.name.encode('utf-8')


class City(models.Model):
    """
    cities do not have district
    districts have district as parent city
    """
    name = models.CharField(max_length=30)
    state = models.ForeignKey(State)
    district = models.ForeignKey("City", blank=True, null=True, related_name='districts')

    def __str__(self):
        return self.name.encode('utf-8')

    class Meta:
        verbose_name_plural = 'Cities'


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category)
    price = models.FloatField(default=0, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(Customer)
    region = models.ForeignKey(City, blank=True, null=True)
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

    def __unicode__(self):
        return self.title


PURCHASE_TYPE = (
    ('direct', 'DIRECT'),
    ('escrow', 'ESCROW')
)

PURCHASE_STATUS = (
    (0, 'FINISHED SUCCESSFULLY'),
    (1, 'WAIT RELEASE'),
    (2, 'UNDER DISPUTE')
)

class PostPurchase(models.Model):
    post = models.ForeignKey(Post)
    purchaser = models.ForeignKey(Customer)
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
    post = models.ForeignKey(Post)
    rater = models.ForeignKey(Customer)
    purchase = models.ForeignKey(PostPurchase, null=True)
    rating = models.FloatField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} - {}'.format(self.post.title, self.rater.username)


class Search(models.Model):
    keyword = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True)
    state = models.ForeignKey(State, blank=True, null=True)
    owner = models.ForeignKey(Customer)
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
    post = models.ForeignKey(Post, related_name='images')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_head = models.BooleanField(default=False)
    
    def __str__(self):
        return '{} - {}'.format(self.post.title, self.name)



class Favourite(models.Model):
    owner =  models.ForeignKey(Customer, related_name="favourites")
    post = models.ForeignKey(Post)

    def __str__(self):
        return '{} - {}'.format(self.owner.first_name, self.post.title)


class Hidden(models.Model):
    owner =  models.ForeignKey(Customer)
    post = models.ForeignKey(Post, related_name='post')

    def __str__(self):
        return '{} - {}'.format(self.owner.first_name, self.post.title)


class Perk(models.Model):
    title = models.CharField(max_length=200)
    campaign = models.ForeignKey("Campaign")
    price = models.IntegerField()
    retail = models.IntegerField(default=0)
    description = models.TextField()
    num_avail = models.IntegerField(default=1000000)
    num_claimed = models.IntegerField(default=0)
    image = models.ImageField(upload_to="perks", blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.campaign.title, self.title)


class PerkClaim(models.Model):
    campaign = models.ForeignKey("Campaign", related_name="claims")
    # null for donate
    perk = models.ForeignKey(Perk, blank=True, null=True, related_name="claims")
    contact = models.TextField(blank=True, null=True)
    # null for Anonymous
    claimer = models.ForeignKey(Customer, blank=True, null=True)
    amount = models.IntegerField()      # in cent
    transaction = models.CharField(max_length=100)

    def __str__(self):
        return self.campaign.title


class CampCategory(models.Model):
    parent = models.ForeignKey("CampCategory", blank=True, null=True)
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
    category = models.ForeignKey(CampCategory)
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
    owner =  models.ForeignKey(Customer)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title
