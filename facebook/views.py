from django.shortcuts import render, redirect
from django.contrib import messages
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
from django.contrib.auth.models import User
from home.models import settingModel2
from home.models import profile, subscription
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import editAdCopyForm, editFbAccountForm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from requests.compat import quote_plus
from selenium.common.exceptions import (
    NoSuchWindowException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    WebDriverException,
    )
from selenium.webdriver.common.action_chains import ActionChains
from .scripts import getDriver, generateCode
from django.contrib.auth.models import User
from .tasks import (
    joinGroupsTask,
    checkIfGroupsApprovedTask,
    StartCompaignTask,
    checkPostedApprovedAndChangeItTask
    )
import random, string, re , os, time
# Create your views here.

def docsView(request):
    doc = Docs.objects.all()
    if len(doc) < 1:
        return redirect('dashboard:dashboard')
    context = {
        'doc':doc[0],
        'title':'documentation'
    }
    return render(request, 'facebook/docs.html', context)

def is_valid(username, password):
    return username != '' and password != ''



@login_required
def facebookAccountsView(request):
    try :
        try:
            try:
                now = timezone.now()
                user = request.user
                my_profile = profile.objects.get(user = user)
                if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
                    if my_profile.profile_subscription.subscription_to > now :
                    
                        fb_accounts = fbAccountsModel.objects.filter(user = request.user, accountStatus = 'active')
                        fb_accounts_to_show = fbAccountsModel.objects.filter(user = request.user)
                        print(fb_accounts)
                        if request.method == 'POST':
                            username = request.POST['username']
                            password = request.POST['password']
                            if username in fb_accounts :
                                messages.warning(request, 'this account is alredy added')
                                return redirect('/facebook/accounts')
                            else:
                                if is_valid(username, password):
                                    chrome_options = webdriver.ChromeOptions()
                                    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
                                    chrome_options.add_argument('headless')
                                    chrome_options.add_argument("--disable-dev-shm-usage")
                                    chrome_options.add_argument("--no-sandbox")
                                    prefs = {"profile.default_content_setting_values.notifications" : 2}
                                    chrome_options.add_experimental_option("prefs",prefs)
                                    driver = None

                                    # try to find the chromdriver in local machin for linux
                                    try:
                                        driver = webdriver.Chrome('facebook/static/facebook/chrom/chromedriver', chrome_options=chrome_options)
                                        driver.get('https://www.facebook.com')
                                    except :
                                        try:
                                            driver = webdriver.Chrome('facebook/static/facebook/chrom/chromedriver1', chrome_options=chrome_options)
                                            driver.get('https://www.facebook.com')
                                        except :
                                            try:
                                                driver = webdriver.Chrome('facebook/static/facebook/chrom/chromedriver2', chrome_options=chrome_options)
                                                driver.get('https://www.facebook.com')
                                            except :
                                                # END try to find the chromdriver in local machin for linux

                                                # try to find the chromdriver in local machin for windows

                                                # END try to find the chromdriver in local machin for windows

                                                # then if did not find it run the one on heroku 
                                                try:
                                                    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)
                                                    driver.get('https://www.facebook.com')
                                                except :                
                                                    return redirect('dashboard:dashboard')
                                                
                                    email = driver.find_element_by_id('email')
                                    fb_password = driver.find_element_by_id('pass')
                                    time.sleep(5)
                                    
                                    for item in username:
                                        email.send_keys(item)
                                    time.sleep(1)
                                    for item in password:
                                        fb_password.send_keys(item)
                                    fb_password.send_keys(Keys.RETURN)
                                    time.sleep(1)
                                    if 'https://www.facebook.com/checkpoint' in driver.current_url or 'https://www.facebook.com/checkpoint/?next' in driver.current_url:
                                        driver.close()
                                        messages.warning(request, 'this account is blocked')
                                        return redirect('fb:facebookAccounts')
                                    else:
                                        pass
                                    try:
                                        error_box = driver.find_element_by_id('error_box')
                                        driver.close()
                                        messages.warning(request, 'username or password is incorrect')
                                        return redirect('/facebook/accounts')
                                    except:
                                        driver.get('https://www.facebook.com/me/')
                                        time.sleep(1)
                                        try:
                                            old_facebook_version = driver.find_element_by_tag_name('h1').text
                                            if old_facebook_version == 'facebook' or old_facebook_version == 'فيسبوك' :
                                                driver.close()
                                                messages.warning(request, 'the facebook account you are trying to add is using the old version of facebook so please turn it to new version')
                                                return redirect('fb:facebookAccounts')
                                        except:
                                            pass
                                        fullname = None
                                        try:
                                            fullname = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[1]')
                                        except:
                                            pass
                                        time.sleep(2)
                                        datOfJoin = None
                                        try:
                                            datOfJoin = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[1]/div/ul/div[2]/div[2]/div')
                                        except:
                                            pass
                                        # groups.ex
                                        if datOfJoin != None and fullname != None:
                                            fbAccountsModel.objects.create(
                                                user = request.user,
                                                username = username,
                                                password = password,
                                                fullname = fullname.text,
                                                dateOfCreating = datOfJoin.text,
                                            )
                                        elif fullname != None:
                                            fbAccountsModel.objects.create(
                                                user = request.user,
                                                username = username,
                                                password = password,
                                                fullname = fullname.text,
                                                dateOfCreating = 'not avalibale',
                                            )
                                        else:
                                            fbAccountsModel.objects.create(
                                                user = request.user,
                                                username = username,
                                                password = password,
                                                fullname = 'not avalibale',
                                                dateOfCreating = 'not avalibale',
                                            )


                                        time.sleep(1)
                                        driver.close()
                                        messages.success(request, 'sucessfully added')
                                        return redirect('/facebook/accounts')
                    else:   
                        messages.warning(request, "your subscription is expired you sould renew it")
                        return redirect('home:subscription')

                else:
                    messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us")
                    return redirect('home:subscription')
                    
            except StaleElementReferenceException:
                messages.warning(request, 'something went wrong please try again')
                driver.close()
                return redirect('/facebook/accounts')
                
        except NoSuchWindowException:
            messages.warning(request, 'please dont close the window until it finished')
            return redirect('/facebook/accounts')
    except NoSuchWindowException:
            messages.warning(request, """something went wrong please try again please theck the status of the account that you are 
            trying to add and make sure it is not blocked or using the old version of fb """)
            return redirect('/facebook/accounts')

    context = {
        'fb_accounts':fb_accounts_to_show,
        'title':'accounts'
    }

    return render(request, 'facebook/facebook_accounts.html', context)

@login_required
def deleteFbAccount(request, pk):
    try:
        now = timezone.now()
        user = request.user
        my_profile = profile.objects.get(user = user)
        if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
            if my_profile.profile_subscription.subscription_to > now :
                fb_account = fbAccountsModel.objects.get(user = request.user, id=pk)
                if request.method == 'POST':
                    fb_account.delete()
                    messages.warning(request, 'sucessfully deleted')
                    return redirect('/facebook/accounts')
                context = {
                    'fb_account':fb_account,
                    'title':'delete accounts'

                }

                return render(request, 'facebook/delete_facebook.html', context)
            else:
                messages.warning(request, "your subscription is expired you sould renew it")
                return redirect('home:subscription')
        else:
            messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
            return redirect('home:subscription')

    except ObjectDoesNotExist:
        messages.warning(request, 'this account is not exists')
        return redirect('/facebook/accounts')

@login_required
def EditFbAccountView(request, pk):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            try :
                my_fb = fbAccountsModel.objects.get(user=request.user, id=pk)
                if request.method == 'POST':
                    unbanded = request.POST.get('unbanded')
                    print(f'unbanded {unbanded}')
                    form = editFbAccountForm(request.POST, instance=my_fb)
                    if form.is_valid():
                        form.save()
                        if unbanded :
                            my_fb.accountStatus = 'active'
                            my_fb.save()
                        messages.success(request, 'sucessfully edited')
                        return redirect('fb:facebookAccounts')
                else:
                    form = editFbAccountForm(instance=my_fb)

                context = {
                    'form':form,
                    'my_fb':my_fb,
                    'title':'edit accounts'

                }
                return render(request, 'facebook/EditFbAccount.html', context)

            except ObjectDoesNotExist:
                messages.warning(request, 'this Fb account is not exisits')
                return redirect('fb:facebookAccounts')
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def addNicheView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :

            niches = nichesModel.objects.filter(user = request.user)

            if request.method == 'POST':
                niche = request.POST.get('niche')
                skip = request.POST.get('join')
                check_if_niche_exists = nichesModel.objects.filter(user = request.user, niche = niche )

                if skip :
                    skip = True
                else :
                    skip = False

                if not check_if_niche_exists.exists():
                    nichesModel.objects.create(
                            user = request.user,
                            niche = niche,
                            skipQuestions = skip
                        )

            context = {
                'niches':niches,
                'title':'niches'

            }

            return render(request, 'facebook/addnich.html', context)
        else:
            
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')
    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def deleteNiche(request, pk):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            try:
                niche = nichesModel.objects.get(user = request.user, id=pk)
                if request.method == 'POST':
                    niche.delete()
                    messages.warning(request, 'sucessfully deleted')
                    return redirect('/facebook/addniche/')

            except ObjectDoesNotExist:
                messages.warning(request, 'Error this niche is not exists')
                return redirect('/facebook/addniche/')

            context = {
                'niche':niche,
                'title':'delete niche'
                
            }
            return render(request, 'facebook/deleteniche.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def groupsView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            
            setting = settingModel2.objects.get(user = request.user)
            wait_after_each_join =  setting.to_wait_after_each_join * 60

            context = {'title':'groups'}
            
            try:  
                fb_accounts = fbAccountsModel.objects.filter(user = request.user, accountStatus = 'active')
                to_test_copy_write = adminCopywrits.objects.all()
                if request.method == 'POST':
                    niches = nichesModel.objects.filter(user = request.user)
                    if len(niches) < 1 :
                        messages.warning(request, 'you dont add any niche')
                        return redirect('/facebook/groups/')
                    if fb_accounts.exists():
                        user_pk=  request.user.id
                        task = joinGroupsTask.delay(user_pk)

                        context = {
                            'data' : task,
                            'task_id':task.task_id,
                            'title':'groups'

                        }

                        return render(request, 'facebook/groups.html',context)
                        
                    else :
                        messages.warning(request, 'you dont add any facebook account')
                        return redirect('/facebook/groups/')
                        
            except :
                messages.warning(request, 'somthing went wrong try again later and make sur dont close the windows before it finished')
                return redirect('/facebook/groups/')

        
            return render(request, 'facebook/groups.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')


    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def deleteGroupView(request, pk):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            try :
                group = myGroupsModel.objects.get(user = request.user, id = pk)
                if request.method == 'POST':
                    group.delete()
                    messages.success(request, 'Successfully deleted')
                    return redirect('dashboard:dashboard')
            except:
                messages.warning(request, 'groups does not exists')
                return redirect('dashboard:dashboard')
            context = {
                'title':'delete group',
                'group':group,
            }
            return render(request, 'facebook/deletegroups.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')
            
@login_required
def checkIfGroupsApproved(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    setting = settingModel2.objects.get(user = request.user)
    wait_after_each_post =  setting.to_wait_after_each_post * 60
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            fb_accounts = fbAccountsModel.objects.filter(user = request.user, accountStatus = 'active')
            to_test_copy_write = adminCopywrits.objects.all()
            if len(fb_accounts) > 0 :
                if request.method == 'POST':
                    user_pk=  request.user.id
                    task = checkIfGroupsApprovedTask.delay(user_pk)
                    context = {
                            'task_id':task.task_id,
                            'title':'group\'s status'
                        }

                    return render(request, 'facebook/CheckGroupsStatus.html',context)
            else:
                messages.warning(request, 'You should add ay least one facebook account and one copywrite')
                return redirect('/facebook/accounts')  

            context = {
                'title':'group\'s status'
            }
            return render(request, 'facebook/CheckGroupsStatus.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')
    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def imageGaleryView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            niches = nichesModel.objects.filter(user=request.user)
            images = imageGalery.objects.filter(user=request.user)
            copy_write = copyWriting.objects.filter(user=request.user)
            if request.method == 'POST':
                image = request.POST.get('img')
                niche = request.POST.get('niche')
                my_niche = nichesModel.objects.filter(user=request.user, niche=niche)
                imageGalery.objects.create(
                    user = request.user,
                    image = image,
                    nich = my_niche[0],
                    str_nich = niche
                )
                
            context = {
                'title':'gellary',
                'niches':niches,
                'images':images,
                'copy_write':copy_write
            }

            return render(request, 'facebook/imagegalery.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def deleteImg(request, pk):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            try:
                image = imageGalery.objects.get(user = request.user, id=pk)
                image.delete()
                messages.warning(request, 'sucessfully deleted')

                return redirect('/facebook/images-galery/')
            except ObjectDoesNotExist:
                messages.warning(request, 'this image is not exisits')
                return redirect('/facebook/images-galery')
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def addCopyWriteView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            if request.method == 'POST':
                discription = request.POST.get('discription')
                niche = request.POST.get('niche')
                my_niche = nichesModel.objects.filter(user=request.user, niche=niche)
                copyWriting.objects.create(
                    user = request.user,
                    description = discription,
                    nich = my_niche[0],
                    str_nich = niche
                )

                messages.success(request, 'succesfully added')
                return redirect('fb:images')
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def deleteCopyWrite(request, pk):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            try:
                copy_write = copyWriting.objects.get(user=request.user, id=pk)
                copy_write.delete()
                messages.warning(request, 'sucessfully deleted')

                return redirect('/facebook/images-galery/')
            except ObjectDoesNotExist:
                messages.warning(request, 'this image is not exisits')
                return redirect('/facebook/images-galery')
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def adCopyView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            my_adcopies = adCopy.objects.filter(user=request.user)
            niches = nichesModel.objects.filter(user=request.user)
            if request.method == 'POST':
                discription = request.POST.get('discription')
                image = request.POST.get('img')
                link = request.POST.get('link')
                niche = request.POST.get('niche')
                my_niche = nichesModel.objects.filter(user=request.user, niche=niche)
                adCopy.objects.create(
                    user = request.user,
                    descriprtion = discription,
                    link = link,
                    image = image,
                    niche = my_niche[0],
                )
                messages.success(request, 'sucessfully added')
                return redirect('/facebook/adcopies/')

            context = {
                'my_adcopies':my_adcopies,
                'niches':niches,
                'titel':'adCopies'
            }

            return render(request, 'facebook/adcopy.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def deleteAdcopy(request, pk):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            try:
                my_adcopies = adCopy.objects.filter(user=request.user, id=pk)
                if request.method == 'POST':
                    my_adcopies.delete()
                    messages.warning(request, 'sucessfully deleted')
                    return redirect('/facebook/adcopies/')

                context = {
                    'my_adcopies':my_adcopies
                }
                return render(request, 'facebook/delete_ad_copy.html', context)
            except ObjectDoesNotExist:
                messages.warning(request, 'this ad copy is not exisits')
                return redirect('/facebook/adcopies')
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def EditAdCopyView(request, pk):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            try :
                niches = nichesModel.objects.filter(user=request.user)
                my_adcopies = adCopy.objects.filter(user=request.user, id=pk)
                if request.method == 'POST':
                    form = editAdCopyForm(request.POST, request.FILES, instance=my_adcopies[0])
                    niche = request.POST.get('niche')
                    print(niche)
                    my_niche = nichesModel.objects.get(user=request.user, niche=niche)
                    if form.is_valid():
                        my_adcopies[0].niche = my_niche
                        my_adcopies[0].save()
                        form.save()
                        messages.success(request, 'sucessfully edited')
                        return redirect('/facebook/adcopies/')
                else:
                    form = editAdCopyForm(instance=my_adcopies[0])
            except ObjectDoesNotExist:
                messages.warning(request, 'this ad copy is not exisits')
                return redirect('/facebook/adcopies')


            context = {
                'my_adcopies':my_adcopies[0],
                'form':form,
                'niches':niches,
                'titel':'edit adCopie'
            }

            return render(request, 'facebook/EditAdcopy.html', context)
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')



@login_required
def startCopmaignView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    setting = settingModel2.objects.get(user = request.user)
    wait_after_each_post =  setting.to_wait_after_each_post * 60
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :

            fb_accounts = fbAccountsModel.objects.filter(user = request.user, accountStatus = 'active')
            my_adCopies = adCopy.objects.filter(user=request.user, used = False)
            posted_and_didnt_approved = postedAdCompaigns.objects.filter(user=request.user, posted=False, done=False)
            all_ad_compains = postedAdCompaigns.objects.filter(user = request.user)
            changing_copyWrite = copyWriting.objects.filter(user=request.user)
            changing_pic = imageGalery.objects.filter(user=request.user)
            for ad in posted_and_didnt_approved :
                if timezone.now() > ad.posted_at + timezone.timedelta(days=2):
                    ad.delete()

            for ad in all_ad_compains :
                if timezone.now() > ad.posted_at + timezone.timedelta(days=10):
                    ad.delete()
            # lenghths 
            fb_len , adCopy_len = len(fb_accounts), len(my_adCopies)
            copWriye_len, pic_len = len(changing_copyWrite), len(changing_pic)
            if request.method == 'POST':   

                if fb_len  > 0 and adCopy_len  > 0 and copWriye_len  > 0 and pic_len  > 0 : 

                    user_pk=  request.user.id
                    task = StartCompaignTask.delay(user_pk)
                    context = {
                            'task_id':task.task_id,
                            'all_ad_compains':all_ad_compains,
                            'title':'campaign',
                        }

                    return render(request, 'facebook/startcampaign.html',context)
                else:
                    messages.warning(request, 'You should add ay least one facebook account, one active ad copy, one image in gallery and one to change with CopyWrite')
                    return redirect('/facebook/adcopies') 
            context = {
                'all_ad_compains':all_ad_compains,
                'title':'campaign'
                }
            return render(request, 'facebook/startcampaign.html', context)
                     
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')

    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

@login_required
def checkPostedApprovedAndChangeItView(request):
    now = timezone.now()
    user = request.user
    my_profile = profile.objects.get(user = user)
    if my_profile.profile_subscription and my_profile.profile_subscription.paid == True and my_profile.subscription_status == 'active':
        if my_profile.profile_subscription.subscription_to > now :
            to_remplace_with = postedAdCompaigns.objects.filter(user=request.user, posted=False, done=False)
            fb_accounts = fbAccountsModel.objects.filter(user = request.user, accountStatus = 'active')
            if len(fb_accounts) > 0:
                for ad in to_remplace_with :
                    if timezone.now() > ad.posted_at + timezone.timedelta(days=2):
                        ad.delete()
                if request.method == 'POST':
                    user_pk=  request.user.id
                    task = checkPostedApprovedAndChangeItTask.delay(user_pk)

                context = {
                    'titel':'waiting approvment posts'
                }
                return render(request, 'facebook/posts_wiating_approvment.html', context)
            else:
                messages.warning(request, "you don't have any active fb accounts")
                return redirect('facebook:facebookAccounts')
        else:
            messages.warning(request, "your subscription is expired you sould renew it")
            return redirect('home:subscription')
    else:
        messages.warning(request, "you don't have a subscription make sure to have one and if you think some thing wrong contact us") 
        return redirect('home:subscription')

