# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *
from .post_models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'column', 'form', 'price']
    search_fields = ['name', 'form']


class CSessionAdmin(admin.ModelAdmin):
    list_display = ['key', 'val']
    search_fields = ['key', 'val']


class CampCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'column']
    search_fields = ['name']


class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sortname']
    search_fields = ['name']


class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    search_fields = ['name']


class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'district']
    search_fields = ['name']


class PerkAdmin(admin.ModelAdmin):
    list_display = ['title', 'campaign', 'num_avail']
    search_fields = ['title']


class PerkClaimAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'perk', 'claimer', 'amount', 'transaction']
    search_fields = ['campaign']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['post', 'rating', 'rater', 'created_at']
    search_fields = ['post']


class PostPurchaseAdmin(admin.ModelAdmin):
    list_display = ['post', 'purchaser', 'type', 'transaction', 'status', 'created_at']
    search_fields = ['post']


class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'created_at', 'is_head']
    list_filter = ['post']
    search_fields = ['name']


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'detail_category', 'category', 'region', 'owner', 'created_at', 'by_dealer']
    search_fields = ['title']

    def detail_category(self, obj):
        return '{}/{}'.format(obj.category.parent, obj.category)


class SearchAdmin(admin.ModelAdmin):
    list_display = ['owner', 'category', 'des_state', 'des_city', 'keyword']

    def des_state(self, obj):
        if obj.state:
            return '{} / {}'.format(obj.state.country.name, obj.state.name)

    def des_city(self, obj):
        if obj.city:
            return '{} / {} / {}'.format(obj.city.state.country.name, obj.city.state.name, obj.city.name)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'provider', 'email', 'phone']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    def provider(self, obj):
        sas = obj.socialaccount_set.all().exclude(provider='stripe')
        if sas:
            return sas[0].provider
        else:
            return '-'

class MessageAdmin(admin.ModelAdmin):
    list_display = ['customer_from', 'customer_to', 'content', 'date', 'status', 'starred', 'post']
    search_fields = ['content']


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(PostPurchase, PostPurchaseAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(GaragePost)
admin.site.register(JobPost)
admin.site.register(CarPost)
admin.site.register(AptPost)
admin.site.register(BoatPost)
admin.site.register(BookPost)
admin.site.register(CDPost)
admin.site.register(CellPhonePost)
admin.site.register(RoomPost)
admin.site.register(MotorCyclePost)
admin.site.register(OfficePost)
admin.site.register(BuyGigPost)
admin.site.register(AntiquePost)
admin.site.register(ShortTermPost)
admin.site.register(SubletPost)
admin.site.register(EventPost)
admin.site.register(AutoWheelPost)
admin.site.register(RealEstatePost)
admin.site.register(LicensePost)
admin.site.register(TicketPost)
admin.site.register(TrailerPost)
admin.site.register(Favourite)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Search, SearchAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(CampCategory, CampCategoryAdmin)
admin.site.register(Campaign)
admin.site.register(Perk, PerkAdmin)
admin.site.register(PerkClaim, PerkClaimAdmin)
admin.site.register(CSession, CSessionAdmin)
admin.site.register(Message, MessageAdmin)