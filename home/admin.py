from django.contrib import admin
from .models import (
    profile,
    subscription,
    settingModel2,
    Coupon
)

class subs(admin.ModelAdmin):
    list_display=[
        'user',
        'paid',
        'subscription_duration',
        'subscription_from',
        'subscription_to'

        ]
    list_filter=[
        'paid',
    ]

class profiles(admin.ModelAdmin):
    list_display=[
        'user',
        'subscription_status',
        'profile_subscription',
        'coupon_code',

        ]
  
# Register your models here.

admin.site.register(profile, profiles)
admin.site.register(subscription, subs)
admin.site.register(settingModel2)
admin.site.register(Coupon)

