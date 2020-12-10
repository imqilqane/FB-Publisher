from django.contrib import admin
from .models import (
    fbAccountsModel,
    myGroupsModel,
    nichesModel,
    imageGalery,
    adCopy,
    copyWriting,
    postedAdCompaigns,
    settingModel,
    adminCopywrits,
    Docs
    )
# Register your models here.

class GroupsAdmin(admin.ModelAdmin):
    list_display=[
        'facebook_account',
        'group_name',
        'approved',
        'posting_with_permestion',

        ]
    list_filter=[
        'approved',
        'posting_with_permestion',

    ]

admin.site.register(fbAccountsModel)
admin.site.register(myGroupsModel, GroupsAdmin)
admin.site.register(nichesModel)
admin.site.register(imageGalery)
admin.site.register(adCopy)
admin.site.register(copyWriting)
admin.site.register(postedAdCompaigns)
admin.site.register(settingModel)
admin.site.register(adminCopywrits)
admin.site.register(Docs)
    
