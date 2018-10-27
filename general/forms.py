# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import ModelForm
from django.forms.utils import ErrorList
from django.forms.formsets import formset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from allauth.utils import generate_unique_username

from .models import *
from .post_models import *

class SignupForm(UserCreationForm):
    def signup(self, request, user):
        data = self.cleaned_data
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.gender = data['gender']
        user.dob = data['dob']
        user.address = data['address']
        user.paypal = data['paypal']

        if 'password1' in data:
            user.set_password(data['password1'])
        else:
            user.set_unusable_password()

        user.username = generate_unique_username([
            data['first_name'],
            data['last_name'],
            data['email'],
            'user'])

        user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2', 'first_name', 
                  'last_name', 'gender', 'dob', 'address')


class CustomerForm(ModelForm):
    # dob = forms.DateTimeField(input_formats='%d-%m-%Y')

    class Meta:
        model = Customer
        exclude = ['password', 'date_joined', 'last_login', 'is_superuser', 
                   'is_staff', 'is_active', 'phone_verified', 'forum_handle',
                   'default_site', 'duration', 'v_statue', 'id_photo']


class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        exclude = ['raised']


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = '__all__'


class JobPostForm(ModelForm):
    class Meta:
        model = JobPost
        fields = '__all__'


class GaragePostForm(ModelForm):
    class Meta:
        model = GaragePost
        fields = '__all__'


class SaleGarageForm(ModelForm):
    class Meta:
        model = SaleGarage
        fields = '__all__'


class CarPostForm(ModelForm):
    class Meta:
        model = CarPost
        fields = '__all__'


class AptPostForm(ModelForm):
    class Meta:
        model = AptPost
        fields = '__all__'


class EventPostForm(ModelForm):
    class Meta:
        model = EventPost
        fields = '__all__'


class RoomPostForm(ModelForm):
    class Meta:
        model = RoomPost
        fields = '__all__'


class OfficePostForm(ModelForm):
    class Meta:
        model = OfficePost
        fields = '__all__'


class BuyGigPostForm(ModelForm):
    class Meta:
        model = BuyGigPost
        fields = '__all__'


class LicensePostForm(ModelForm):
    class Meta:
        model = LicensePost
        fields = '__all__'


class RealEstatePostForm(ModelForm):
    class Meta:
        model = RealEstatePost
        fields = '__all__'


class SubletPostForm(ModelForm):
    class Meta:
        model = SubletPost
        fields = '__all__'


class AntiquePostForm(ModelForm):
    class Meta:
        model = AntiquePost
        fields = '__all__'


class AutoWheelPostForm(ModelForm):
    class Meta:
        model = AutoWheelPost
        fields = '__all__'


class BoatPostForm(ModelForm):
    class Meta:
        model = BoatPost
        fields = '__all__'


class BookPostForm(ModelForm):
    class Meta:
        model = BookPost
        fields = '__all__'


class CDPostForm(ModelForm):
    class Meta:
        model = CDPost
        fields = '__all__'


class CellPhonePostForm(ModelForm):
    class Meta:
        model = CellPhonePost
        fields = '__all__'


class MotorCyclePostForm(ModelForm):
    class Meta:
        model = MotorCyclePost
        fields = '__all__'


class TicketPostForm(ModelForm):
    class Meta:
        model = TicketPost
        fields = '__all__'


class TrailerPostForm(ModelForm):
    class Meta:
        model = TrailerPost
        fields = '__all__'


class ShortTermPostForm(ModelForm):
    class Meta:
        model = ShortTermPost
        fields = '__all__'


class SearchForm(ModelForm):
    class Meta:
        model = Search
        fields = '__all__'

