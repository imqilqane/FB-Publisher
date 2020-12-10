from django.contrib import admin
from .models import (
    profile,
    subscription,
    settingModel2,
    Coupon
)
# Register your models here.

admin.site.register(profile)
admin.site.register(subscription)
admin.site.register(settingModel2)
admin.site.register(Coupon)

