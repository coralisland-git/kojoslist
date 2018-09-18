"""kojoslist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from general.views import *

admin.site.site_header = "Globalboard Admin"

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
]


urlpatterns += [
    url(r"^$", index, name="index"),
    # url(r"^home$", home, name="home"),
    url(r"^delete_ads$", delete_ads, name="delete_ads"),
    url(r"^delete_camp$", delete_camp, name="delete_camp"),
    url(r"^breadcrumb$", breadcrumb, name="breadcrumb"),
    url(r"^search_ads$", search_ads, name="search_ads"),
    url(r"^rate_ads$", rate_ads, name="rate_ads"),
    url(r"^update_alert$", update_alert, name="update_alert"),
    url(r"^search_camps$", search_camps, name="search_camps"),    
    url(r"^active_deactive_ads", active_deactive_ads, name="active_deactive_ads"),
    url(r"^get_post_detail$", get_post_detail, name="get_post_detail"),
    url(r"^profile", profile, name="profile"),
    url(r"^toggle_favourite", toggle_favourite, name="toggle_favourite"),
    url(r"^my-ads", my_ads, name="my-ads"),
    url(r"^explorer-campaigns", explorer_campaigns, name="explorer-campaigns"),
    url(r"^my-campaigns", my_campaigns, name="my-campaigns"),
    url(r"^my-favourites", my_favourites, name="my-favourites"),
    url(r"^my-subscriptions$", my_subscriptions, name="my-subscriptions"),
    url(r"^subscriptions/(?P<ss_id>\d*)$", edit_subscription, name="edit-subscription"),
    url(r"^post-ads/(?P<ads_id>\d*)", post_ads, name="post-ads"),
    url(r"^post-camp/(?P<camp_id>\d*)", post_camp, name="post-camp"),
    url(r"^ads/(?P<ads_id>\d*)", view_ads, name="view-ads"),
    url(r"^user_show/(?P<user_id>\d*)", user_show, name="user review"),
    url(r"^campaigns/(?P<camp_id>\d*)", view_campaign, name="view-campaign"),
    url(r"^category-ads/(?P<category_id>\d*)", category_ads, name="category-ads"),
    url(r"^category-ads-dealer/(?P<category_id>\d*)/(?P<kind>.*)", category_ads_dealer, name="category-ads-dealer"),
    url(r"^upload-image$", upload_image, name="upload-image"),
    url(r"^delete-image$", delete_image, name="delete-image"),
    url(r"^get_sub_info$", get_sub_info, name="get_sub_info"),
    url(r"^logout$", ulogout, name="logout"),
    url(r"^region-ads/st/(?P<region_id>\d+)", region_ads, {'region': 'state'}, name="state-ads"),
    url(r"^region-ads/ct/(?P<region_id>\d+)", region_ads, {'region': 'city'}, name="city-ads"),
    url(r"^region-ads/wd/(?P<region_id>\d*)", region_ads, {'region': 'world'}, name="world-ads"),
    url(r"^get_regions", get_regions, name="get_regions"),
    url(r"^verify_phone", verify_phone, name="verify_phone"),   
    url(r"^confirm-phone", confirm_phone, name="confirm-phone"),   
    url(r"^send_vcode", send_vcode, name="send_vcode"),   
    url(r"^upload_id", upload_id, name="upload_id"),   
    url(r"^about", about, name="about"),   
    url(r"^faq", faq, name="faq"),   
    url(r"^contact-us", contact_us, name="contact-us"),   
    url(r"^how-it-works", how_it_works, name="how-it-works"),   
    url(r"^why-global-board", why_global_board, name="why-global-board"),   
    url(r"^terms-of-use", terms_of_use, name="terms-of-use"), 
    url(r"^why-use", why_use, name="why-use"),     
    url(r"^customer-support", customer_support, name="customer-support"),           
    url(r"^my-account", my_account, name="my-account"),   
    url(r"^send_friend_email", send_friend_email, name="send_friend_email"), 
    url(r"^send_reply_email", send_reply_email, name="send_reply_email"),        
    url(r"^create-subscription", create_subscription, name="create-subscription"),        
    url(r"^remove-subscription", remove_subscription, name="remove-subscription"), 
    url(r"^release_purchase", release_purchase, name="release_purchase")
]