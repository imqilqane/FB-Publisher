from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from facebook.models import (
    fbAccountsModel, 
    myGroupsModel,
    adCopy,
    copyWriting,
    imageGalery,
    nichesModel
)
from home.models import profile, subscription
from django.utils import timezone
from django.contrib import messages



# Create your views here.


@login_required
def dashboardView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            fb_accounts = fbAccountsModel.objects.filter(user = request.user)
            groups = myGroupsModel.objects.filter(user = request.user)
            ad_copies = adCopy.objects.filter(user = request.user)
            images = imageGalery.objects.filter(user = request.user)
            copy_writes = copyWriting.objects.filter(user = request.user)
            groups_per_niche = []
            cercelar_char_elements = []
            for group in groups:
                groups_per_niche.append(group.group_nich)
            
            groups_per_niche.sort()

            counter = 0
            index = 0
            try:
                cercelar_char_elements.append([groups_per_niche[0],0])
            except IndexError:
                cercelar_char_elements.append(['No data to show',100])

            for item in groups_per_niche[1:]:
                if groups_per_niche[index] != item:
                    cercelar_char_elements.append([item,0])
                    counter = 0
                else:
                    counter += 1
                    cercelar_char_elements[len(cercelar_char_elements)-1][1] = counter +1
                index += 1

            json_cercelar_char_elements = json.dumps(cercelar_char_elements)

            
            context = {
                'fb_accounts':fb_accounts,
                'groups':groups,
                'groups_len':len(groups),
                'accepted_groups_len':len(groups.filter(approved=True)),
                'waiting_groups_len':len(groups.filter(approved=False)),
                'no_admin':len(groups.filter(approved=True, posting_with_permestion = False)),
                'admin':len(groups.filter(approved=True, posting_with_permestion = True )),
                'ad_copies_len':len(ad_copies),
                'images_len':len(images),
                'copy_writes_len':len(copy_writes),
                'json_cercelar_char_elements':json_cercelar_char_elements,
                'title' : 'home'
            }

            if not request.user.is_active:
                context.update({'not_active_user':True})
                
            return render(request, 'dashboard/dashboard.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')


def addGroupToFavorate(request, pk):
    group = myGroupsModel.objects.get(user = request.user, id=pk)

    group.favorated = True
    group.save()
    messages.success(request,'group is added to favorated list')
    return redirect('dashboard:dashboard')

def removeGroupfromFavorate(request, pk):
    group = myGroupsModel.objects.get(user = request.user, id=pk)

    group.favorated = False
    group.save()
    messages.success(request,'group is removed from favorated list')
    return redirect('dashboard:dashboard')