from celery import shared_task
from django.shortcuts import render, redirect
from django.contrib import messages
from celery_progress.backend import ProgressRecorder
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from requests.compat import quote_plus
from django.contrib.auth.models import User
from selenium.common.exceptions import (
    NoSuchWindowException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    WebDriverException,
    )
from selenium.webdriver.common.action_chains import ActionChains
from django.utils import timezone
from .models import (
    myGroupsModel, 
    fbAccountsModel, 
    adminCopywrits, 
    nichesModel , 
    postedAdCompaigns,
    adCopy,
    copyWriting,
    imageGalery,
    )
from home.models import settingModel2
from .scripts import getDriver , generateCode
import time, re, random


@shared_task(bind=True)
def joinGroupsTask(self, pk):
    request_user = User.objects.get(id = pk)
    # get the request user

    setting = settingModel2.objects.get(user = request_user)
    # get user settings

    join_groups_limits_per_fb = setting.group_join_per_time
    # number of groups to join per fb for this user

    niches = nichesModel.objects.filter(user = request_user)
    # this user niches

    limit_for_niche = setting.group_join_per_time // len(niches)
    # number of groups to join per niche for this user

    wait_after_each_join =  setting.to_wait_after_each_join * 60
    # time to wait after each join

    fb_accounts = fbAccountsModel.objects.filter(user = request_user, accountStatus = 'active')
    # this user active fb account

    to_test_copy_write = adminCopywrits.objects.all()
    # copy right to post in groups that we are in to see posting permession

    total_of_the_loops = limit_for_niche * len(niches) * len(fb_accounts) 
    # how much the loop our fun will do keeping in mind the Nested Loops

    old_persontage = 0
    # this is the base persontage that we will keep adding to it for finishing 100%

    persontage_to_add = persontage_to_add = 99 / total_of_the_loops
    # how much persontage to add to progress bar  (its 99 cause we will ad one imidiatly)

    progress = ProgressRecorder(self)
    # this is the progress bar class

    progress.set_progress(1, 100)
    # add this 1 for just let the bar shows to the user

    old_persontage += 1

    data = {}
    for fb in fb_accounts :
        driver = getDriver(fb)
        if 'https://www.facebook.com/checkpoint' in driver.current_url or 'https://www.facebook.com/checkpoint/?next' in driver.current_url:
            fb.accountStatus = 'Blocked'
            fb.save()   
            continue
        try:
            error_box = driver.find_element_by_id('error_box')
            fb.accountStatus = 'Unactive'
            fb.save()
            continue
        except:
            driver.get('https://www.facebook.com/me/')
            time.sleep(1)
            try:
                old_facebook_version = driver.find_element_by_tag_name('h1').text
                if old_facebook_version == 'facebook' or old_facebook_version == 'فيسبوك' :
                    fb.accountStatus = 'Old fb version'
                    fb.save()
                    continue
            except:
                pass
        groups_am_in_or_sent_request_to_list = []
        groups_am_in_or_sent_request_to = myGroupsModel.objects.filter(user = request_user, facebook_account = fb)
        for group in groups_am_in_or_sent_request_to :
            groups_am_in_or_sent_request_to_list.append(group.group_link)
        data[fb.username] = {'need_awnsers': [],'send_request':[]}
        limit_for_fb_account = 0
        
        for niche in niches:
            quoted_nich = quote_plus(niche.niche)
            link = f"https://www.facebook.com/search/groups/?q={quoted_nich}"
            driver.get(link)
            time.sleep(1)
            page = driver.find_element_by_tag_name('html')
            for scroll in range(15):
                page.send_keys(Keys.END)
                time.sleep(1.5)
            groups_section = None
            while groups_section == None:
                try:
                    groups_section = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[2]/div')
                except:
                    groups_section = None
            links =  groups_section.find_elements_by_tag_name('a')
            groups_links = []
            for group_link in links : 
                if 'groups' in group_link.get_attribute("href") and group_link.get_attribute("href") not in groups_links:
                    if '?q=' not in group_link.get_attribute("href"):
                        groups_links.append(group_link.get_attribute("href"))
            if limit_for_fb_account >= setting.group_join_per_time :
                break
            count = 0
            for group_link_two in groups_links :
                

                if count >= limit_for_niche :
                    break
                if group_link_two not in groups_am_in_or_sent_request_to_list:
                    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')  
                    driver.get(group_link_two)
                    time.sleep(2)
                    group_name = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div[1]/div/div/div[1]/h2/span')
                    
                    try :
                        # this will work if the user is not in the groupe 
                        join = driver.find_element_by_xpath('//*[@aria-label="Join Group"]')
                        join.click()
                        time.sleep(3)
                        try:    
                            # this will work if facebook shows a pop uo tells that you need to choise if you wanna join by profile or page if you have some
                            choose_how_to_join = None
                            choose_how_to_join_limits = 0
                            while choose_how_to_join == None and choose_how_to_join_limits < 4:
                                try:
                                    choose_how_to_join = driver.find_element_by_xpath('//*[@aria-label="Choose How to Join Group"]')
                                except:
                                    choose_how_to_join = None
                                    choose_how_to_join_limits += 1
                                    time.sleep(4)
                            subscription_profile = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div[1]/div/div/div[2]/div[2]/div/div/div').click()
                            apply = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div[4]/div/div/div/div[1]/div[1]')
                            apply.click()
                            
                        except:
                            pass
                        time.sleep(2)
                        
                        if niche.skipQuestions == False:
                            # this will work if the user dont wanna join all groups and skip awnsering the questions
                            try:
                                # if he find QA he will close it and cancel the request 
                                questions_pop_up = None
                                questions_pop_up_limits = 0
                                while questions_pop_up == None and questions_pop_up_limits < 4:
                                    try:
                                        questions_pop_up = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div')
                                    except:
                                        questions_pop_up = None
                                        questions_pop_up_limits += 1
                                        time.sleep(4)
                                if questions_pop_up != None:
                                    data[fb.username]['need_awnsers'].append([group_link_two, group_name.text])
                                    time.sleep(1)          
                                    close = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[2]')
                                    close.click()
                                    time.sleep(1)
                                    exit_without_awnser = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div[2]/div[2]').click()
                                    cancel = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[3]/div/div/div/div[2]/div/div/div[1]/div').click()
                                else:
                                    # this is just to cause and error to pass to the excepte
                                    driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div')
                            except:
                                    # if he dont find QA he wont cancel the request and he will add the groups to sent request list
                                    data[fb.username]['send_request'].append([group_link_two, group_name.text])
                                    myGroupsModel.objects.create(
                                        user = request_user,
                                        facebook_account = fb ,
                                        group_name = group_name.text,
                                        group_nich = niche,
                                        group_link = group_link_two ,
                                    )
                                    progress.set_progress(old_persontage + persontage_to_add, 100)
                                    # adding the persontage to the class for real

                                    old_persontage += persontage_to_add
                                    # add the persentage here

                                    limit_for_fb_account += 1
                                    count += 1
                                    time.sleep(wait_after_each_join)
                        else:
                            # if the user wanna join all groups he will skip closing the qa pop up
                            data[fb.username]['send_request'].append([group_link_two, group_name.text])
                            myGroupsModel.objects.create(
                                user = request_user,
                                facebook_account = fb ,
                                group_name = group_name.text,
                                group_nich = niche,
                                group_link = group_link_two ,
                            )
                
                            limit_for_fb_account = 0
                            count += 1
                            time.sleep(wait_after_each_join)
                                                                    
                    except : 
                        pass
                    try:
                        # this will work if the user is on the group
                        invite = driver.find_element_by_xpath('//*[@aria-label="Invite"]')
                        this_group = myGroupsModel.objects.create(
                            user = request_user,
                            facebook_account = fb ,
                            group_name = group_name.text,
                            group_nich = niche,
                            group_link = group_link_two ,
                            approved = True,
                        )
                        ### need to check posting permestion ###
                        time.sleep(2)
                        add_post_button = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div[1]/div[1]/div/div/div/div[1]/div')
                        add_post_button.click()
                        posting = None
                        while posting is None:
                            try:
                                posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                            except:
                                posting = None
                        used_copy_Write = random.choices(to_test_copy_write)
                        actions = ActionChains(driver)
                        for item in used_copy_Write[0].copy:
                            actions.send_keys(item)
                        actions.perform()
                        time.sleep(2)
                        posting.click()

                        progress.set_progress(old_persontage + persontage_to_add, 100)
                        # adding the persontage to the class for real
                        old_persontage += persontage_to_add
                        # add the persentage here

                        limit_for_fb_account += 1
                        count += 1
                        time.sleep(wait_after_each_join)
                        data[fb.username]['send_request'].append([group_link_two, group_name.text])
                        ############################################################
                        # this will work if fb account get banded from posting
                        try : 
                            posting = None
                            limits = 0
                            while posting == None and limits < 9:
                                try :
                                    posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                    time.sleep(30)
                                    limits += 1
                                    posting = None
                                except:
                                    posting = True
                            if posting == None:   
                                fb.accountStatus = 'banded from posting'
                                fb.save()
                                break
                        except:
                            pass
                        
                        ############################################################
                        
                        post = None
                        trys = 0
                        while post is None and trys < 60:
                            try:
                                post = driver.find_element_by_xpath('//*[@aria-posinset="1"]')
                            except:
                                post = None
                                time.sleep(1)
                                trys += 1
                        post_autor = post.find_element_by_tag_name('h2').text
                        if fb.fullname in post_autor :
                            this_group.posting_with_permestion = False
                            this_group.save()
                        else:
                            this_group.posting_with_permestion = True
                            this_group.save()
                        ########################################
                    except:
                        pass
                time.sleep(5)
                
    driver.close()
    return data


@shared_task(bind=True)
def checkIfGroupsApprovedTask(self, pk):

    request_user = User.objects.get(id = pk)
    # get the request user

    setting = settingModel2.objects.get(user = request_user)
    # get user settings

    to_test_copy_write = adminCopywrits.objects.all()
    # copy right to post in groups that we are in to see posting permession

    wait_after_each_post =  setting.to_wait_after_each_post * 60
    # time to wait after each post

    fb_accounts = fbAccountsModel.objects.filter(user = request_user, accountStatus = 'active')
    # this user active fb account

    user_all_groups_len = len(myGroupsModel.objects.filter(user = request_user, approved=False))
    # we will use that to set the progress

    old_persontage = 0
    # this is the base persontage that we will keep adding to it for finishing 100%

    persontage_to_add = persontage_to_add = 99 / user_all_groups_len
    # how much persontage to add to progress bar  (its 99 cause we will ad one imidiatly)

    progress = ProgressRecorder(self)
    # this is the progress bar class

    progress.set_progress(1, 100)
    # add this 1 for just let the bar shows to the user

    old_persontage += 1


    for fb in fb_accounts :
        request_sent = myGroupsModel.objects.filter(facebook_account = fb, approved=False)
        if len(request_sent) > 0:
            
            driver = getDriver(fb)
            if 'https://www.facebook.com/checkpoint' in driver.current_url or 'https://www.facebook.com/checkpoint/?next' in driver.current_url:
                fb.accountStatus = 'Blocked'
                fb.save()   
                continue
            try:
                error_box = driver.find_element_by_id('error_box')
                fb.accountStatus = 'Unactive'
                fb.save()
                continue
            except:
                driver.get('https://www.facebook.com/me/')
                time.sleep(1)
                try:
                    old_facebook_version = driver.find_element_by_tag_name('h1').text
                    if old_facebook_version == 'facebook' or old_facebook_version == 'فيسبوك' :
                        fb.accountStatus = 'Old fb version'
                        fb.save()
                        continue
                except:
                    pass
            for group in request_sent:
                driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')  
                driver.get(f"{group.group_link}")
                
                time.sleep(3)
                
                try:
                    # this will work if group band the user
                    driver.find_element_by_xpath('//*[@aria-label="Go to News Feed"]')
                    group.active = False
                    group.save()
                    continue
                except:
                    pass
                try:
                    time.sleep(10)
                    trying_limits = 0
                    invite = None
                    while invite == None and trying_limits < 5 :
                        # we loop to give 5 chances to find invit butoon
                        try:
                            invite = driver.find_element_by_xpath('//*[@aria-label="Invite"]')
                        except :
                            time.sleep(5)
                            invite = None
                            trying_limits += 1

                    if invite == None:
                        # we will cause an error if we did not find the invit button so we go out the try
                        driver.find_element_by_xpath('//*[@aria-label="Invite"]')

                    group.approved = True
                    group.save()
                    time.sleep(2)
                    add_post_button = None
                    while add_post_button is None:
                        try:
                            add_post_button = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div[1]/div[1]/div/div/div/div[1]/div')
                        except:
                            add_post_button = None

                    add_post_button.click()

                    posting = None
                    while posting is None:
                        try:
                            posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                        except:
                            posting = None
                    used_copy_Write = random.choices(to_test_copy_write)
                    actions = ActionChains(driver)
                    
                    for item in used_copy_Write[0].copy:
                        actions.send_keys(item)
                    actions.perform()
                    time.sleep(2)
                    posting.click()
                    ############################################################
                    # this will work if fb account get banded from posting
                    try : 
                        posting = None
                        limits = 0
                        while posting == None and limits < 9:
                            try :
                                posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                time.sleep(30)
                                limits += 1
                                posting = None
                            except:
                                posting = True
                        if posting == None:   
                            fb.accountStatus = 'banded from posting'
                            fb.save()
                            break
                    except:
                        pass
                        
                    #########################################################
                    
                    post = None
                    post_tries = 0
                    while post is None and post_tries < 5:
                        try:
                            post = driver.find_element_by_xpath('//*[@aria-posinset="1"]')
                            post_autor = post.find_element_by_tag_name('h2').text
                            if fb.fullname not in post_autor:
                                time.sleep(4)
                                post = None
                                post_tries += 1
                        except:
                            post = None
        
                    if fb.fullname in post_autor :
                        group.posting_with_permestion = False
                        group.save()
                    else:
                        group.posting_with_permestion = True
                        group.save()
                    time.sleep(3)

                    # time to wait after each post
                    time.sleep(wait_after_each_post)
                except:
                    try:
                        join = driver.find_element_by_xpath('//*[@aria-label="Join Group"]')
                        group.delete()
                    except:
                        if timezone.now() > (group.date_of_request + timezone.timedelta(days=3)):
                            group.delete()
                        else:
                            pass

                progress.set_progress(old_persontage + persontage_to_add, 100)
                # adding the persontage to the class for real
                old_persontage += persontage_to_add
                # add the persentage here
        else:
            continue
    driver.close()
    return 'Done'


@shared_task(bind=True)
def StartCompaignTask(self, pk):
    
    request_user = User.objects.get(id = pk)
    # get the request user

    setting = settingModel2.objects.get(user = request_user)
    # get user settings

    to_test_copy_write = adminCopywrits.objects.all()
    # copy right to post in groups that we are in to see posting permession

    wait_after_each_post =  setting.to_wait_after_each_post * 60
    # time to wait after each post

    fb_accounts = fbAccountsModel.objects.filter(user = request_user, accountStatus = 'active')
    # this user active fb account

    user_all_groups_len = len(myGroupsModel.objects.filter(user = request_user, approved=False))
    # we will use that to set the progress

    my_adCopies = adCopy.objects.filter(user=request_user, used = False)
    # tha ad copies that i need to post in
        
    changing_copyWrite = copyWriting.objects.filter(user=request_user)
    # the copyWrite that i will use to muniplate groups admin
    
    changing_pic = imageGalery.objects.filter(user=request_user)
    # the Pics that i will use to muniplate groups admin

    old_persontage = 0
    # this is the base persontage that we will keep adding to it for finishing 100%

    persontage_to_add = persontage_to_add = 99 / setting.post_per_time 
    # how much persontage to add to progress bar  (its 99 cause we will ad one imidiatly)

    progress = ProgressRecorder(self)
    # this is the progress bar class

    progress.set_progress(1, 100)
    # add this 1 for just let the bar shows to the user

    old_persontage += 1


    # start the code

    for ad_copy in my_adCopies:
        for ad_copy in my_adCopies:
            for fb in fb_accounts:
                posting_limits = 0
                driver = getDriver(fb)

                # check if the fb blocked our account
                if 'https://www.facebook.com/checkpoint' in driver.current_url or 'https://www.facebook.com/checkpoint/?next' in driver.current_url:
                    fb.accountStatus = 'Blocked'
                    fb.save()   
                    continue

                # check if the password change
                try:
                    error_box = driver.find_element_by_id('error_box')
                    fb.accountStatus = 'Unactive'
                    fb.save()
                    continue

                # check if the facebook using the new version
                except:
                    driver.get('https://www.facebook.com/me/')
                    time.sleep(1)
                    try:
                        old_facebook_version = driver.find_element_by_tag_name('h1').text
                        if old_facebook_version == 'facebook' or old_facebook_version == 'فيسبوك' :
                            fb.accountStatus = 'Old fb version'
                            fb.save()
                            continue
                    except:
                        pass

                # if the facebook post pass limits
                if posting_limits >= setting.post_per_time :
                    break

                user_groups = myGroupsModel.objects.filter(user = request_user, facebook_account = fb, approved = True, )
                user_groups_len = len(user_groups)

                # if the fb have groups more than 0
                if user_groups_len > 0:

                    # get groups with no posting approvment
                    groups_with_no_admin = myGroupsModel.objects.filter(
                        user = request_user,
                        facebook_account = fb,
                        approved = True, 
                        active = True,
                        group_nich = ad_copy.niche,
                        posting_with_permestion = False,
                        )

                    # get groups with  posting approvment
                    groups_with_admin = myGroupsModel.objects.filter(
                        user = request_user,
                        facebook_account = fb,
                        approved = True, 
                        active = True,
                        group_nich = ad_copy.niche,
                        posting_with_permestion = True,
                        )

                    if len(groups_with_no_admin) > 0:

                        # loop trough the groups that did not need admin approvment
                        for group in groups_with_no_admin:
                            
                            # if we pass the posting limits we will break the loop to pass to the biggest loop
                            if posting_limits  >= setting.post_per_time :
                                break
                            
                            # check if this ad posted before in this groups
                            try :
                                this_ad_alredy_posted_in_this_group = postedAdCompaigns.objects.get(
                                    user=request_user, 
                                    adcopy = ad_copy , 
                                    posting_group = group
                                    )
                                continue
                            except:
                                pass
                            
                            # open new window and get to the group link
                            driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')  
                            driver.get(f"{group.group_link}")
                            time.sleep(2)

                            # this will work if group band the user
                            try:
                                driver.find_element_by_xpath('//*[@aria-label="Go to News Feed"]')
                                group.active = False
                                group.save()
                                continue
                            except:
                                pass

                            # if the ad copy that we are posting did not have image 
                            if not ad_copy.image :

                                # get the add post button and click it then sleep for a while
                                add_post_button = None
                                trys = 0
                                while add_post_button is None and trys < 30:
                                    try:
                                        add_post_button = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]
                                        /div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div[1]/div[1]/div/div/div/div[1]/div""")
                                    except :
                                        add_post_button = None
                                        time.sleep(2)
                                    trys += 1                     
                                add_post_button.click()
                                time.sleep(12)
                                
                                # while the typing marker is read, write the adcopy and the link and post it then sleep for a while
                                actions = ActionChains(driver)
                                for item in ad_copy.descriprtion:
                                    time.sleep(0.05)
                                    actions.send_keys(item)
                                actions.send_keys(Keys.RETURN)
                                for item in ad_copy.link:
                                    actions.send_keys(item)
                                actions.perform()
                                time.sleep(2)
                                posting = driver.find_element_by_xpath('//*[@aria-label="Post"]').click()
                                time.sleep(4)
                            
                            # if the ad copy that we are posting  have image 
                            else:

                                #  get the upload_img input 
                                upload_img = None
                                while upload_img is None :
                                    try:
                                        upload_img = driver.find_element_by_xpath("//input[@type='file']")
                                    except :
                                        upload_img = None

                                # define punsh of vars  
                                to_change_copyWrite = copyWriting.objects.filter(user=request_user, str_nich = group.group_nich)
                                to_change_pic = imageGalery.objects.filter(user=request_user, str_nich = group.group_nich)
                                used_copy_Write = random.choices(to_change_copyWrite)
                                used_copy_image = random.choices(to_change_pic)
                                code = generateCode()

                                # try to upload the image and in case image did not find in that path som move to the except
                                try:
                                    # upload the image and sleep
                                    upload_img.send_keys(used_copy_image[0].image)
                                    time.sleep(10)

                                    # get the posting button
                                    posting = None
                                    while posting == None:
                                        try : 
                                            posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                        except:
                                            posting = None
                                    time.sleep(5)

                                    # while the typing marker is read, write the adcopy and the link and post it then sleep for a while
                                    actions = ActionChains(driver)
                                    for item in ad_copy.descriprtion:
                                        time.sleep(0.05)
                                        actions.send_keys(item)
                                    actions.send_keys(Keys.RETURN)
                                    for item in ad_copy.link:
                                        actions.send_keys(item)
                                    actions.perform()
                                    time.sleep(2)
                                    posting = driver.find_element_by_xpath('//*[@aria-label="Post"]').click()
                                    time.sleep(4)
                                    
                                    # post
                                    posting.click()
                                
                                except:
                                    # delete that path cause it is not working
                                    used_copy_image.delete()
                                    
                                    # get the add post button and click it then sleep for a while
                                    add_post_button = None
                                    trys = 0
                                    while add_post_button is None and trys < 30:
                                        try:
                                            add_post_button = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]
                                            /div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div[1]/div[1]/div/div/div/div[1]/div""")
                                        except :
                                            add_post_button = None
                                            time.sleep(2)
                                        trys += 1                     
                                    add_post_button.click()
                                    time.sleep(12)

                                    # get the posting button
                                    posting = None
                                    while posting == None:
                                        try : 
                                            posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                        except:
                                            posting = None
                                    time.sleep(5)

                                    # while the typing marker is read, write the adcopy and the link and post it then sleep for a while
                                    actions = ActionChains(driver)
                                    for item in ad_copy.descriprtion:
                                        time.sleep(0.05)
                                        actions.send_keys(item)
                                    actions.send_keys(Keys.RETURN)
                                    for item in ad_copy.link:
                                        actions.send_keys(item)
                                    actions.perform()
                                    time.sleep(2)
                                    posting = driver.find_element_by_xpath('//*[@aria-label="Post"]').click()
                                    time.sleep(4)
                                    
                                    # post
                                    posting.click()





                            # this will work if fb account get banded from posting
                            try : 
                                posting = None
                                limits = 0
                                while posting == None and limits < 9:
                                    try :
                                        posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                        time.sleep(30)
                                        limits += 1
                                        posting = None
                                    except:
                                        posting = True
                                if posting == None:   
                                    fb.accountStatus = 'banded from posting'
                                    fb.save()
                                    break
                            except:
                                pass
                            

                            # looking 1st post author
                            post = None
                            trying_limit = 0
                            trys = 0
                            while post is None and trys < 60:
                                try:
                                    post = driver.find_element_by_xpath('//*[@aria-posinset="1"]')
                                    post_autor = post.find_element_by_tag_name('h2').text
                                    if fb.fullname not in post_autor and trying_limit < 12:
                                        time.sleep(5)
                                        post = None 
                                except:
                                    post = None
                                    trys += 1
                                    time.sleep(1)
                                trying_limit += 1
                            
                            # if 1 post author is the fb account user
                            if fb.fullname in post_autor :

                                # change group posting permetion
                                group.posting_with_permestion = False
                                group.save()

                            else:
                                # if this group posting permetion turn to need admin approvment change it and continue 
                                group.posting_with_permestion = True
                                group.save()
                                postedAdCompaigns.objects.create(
                                    user = request_user ,
                                    adcopy = ad_copy,
                                    posting_group = group,
                                    fb_account = fb,
                                )
                                time.sleep(wait_after_each_post)
                                continue
                            
                            # see if the group is public so the posts can be shared
                            # get the share button
                            element = None
                            element_tries = 0
                            while element == None and element_tries <= 5:
                                try:
                                    element = post.find_element_by_xpath('//*[@aria-label="Send this to friends or post it on your Timeline."]')
                                except:
                                    element = None
                                    time.sleep(5)
                                    element_tries += 1

                            # if group is public
                            if element != None:
                                # click share and try to share it win messanger
                                driver.execute_script("arguments[0].click();", element)
                                time.sleep(2)
                                send_in_messanger = None
                                while send_in_messanger == None:
                                    try:
                                        send_in_messanger = post.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]
                                        /div[1]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/
                                        div[1]/div/div[3]/div""")
                                    except:
                                        send_in_messanger = None
                                send_in_messanger.click()
                                time.sleep(2)
                                message_pop_up = None
                                while message_pop_up is None:
                                    try:
                                        message_pop_up = driver.find_element_by_xpath('//*[@aria-label="Send in Messenger"]')
                                    except:
                                        message_pop_up = None
                                
                                # get the post link and creat the postedAdCompaigns
                                post_link = None
                                while post_link is None:
                                    try:
                                        post_link = message_pop_up.find_element_by_xpath("""//*[@id="mount_0_0"]/div/
                                        div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div[3]
                                        /div[1]/div/div/div[1]/div[1]""")                    
                                    except:
                                        post_link = None
                                postedAdCompaigns.objects.create(
                                    user = request_user ,
                                    adcopy = ad_copy,
                                    posting_group = group,
                                    fb_account = fb,
                                    posted = True ,
                                    post_link = post_link.text
                                )

                            # if the group is privte
                            else:

                                # get all the links from the first post
                                try:
                                    tries = 0
                                    post_links = None
                                    post_link_list = []
                                    while post_links == None and tries < 10:
                                        try:
                                            post_links = post.find_elements_by_tag_name('a')
                                            for i in post_links :
                                                post_link_list.append(i.get_attribute("href"))
                                        except:
                                            post_links = None
                                            time.sleep(4)
                                            tries += 1

                                    # if the link has gm. so it is the post link but need edits
                                    photo_link = None
                                    for j in post_link_list:
                                        if 'gm.' in j:
                                            photo_link = j 
                                            break

                                    # find the pure post link and create postedAdCompaigns with link
                                    pattren = '[gm\.]([0-9]+)'
                                    link = re.findall(pattren, photo_link)
                                    full_link = group.group_link  + 'permalink/' + link[0]
                                    postedAdCompaigns.objects.create(
                                        user = request_user ,
                                        adcopy = ad_copy,
                                        posting_group = group,
                                        fb_account = fb,
                                        posted = True ,
                                        post_link = full_link
                                    )
                                
                                # if we cant have the link create postedAdCompaigns with no link but posted
                                except:
                                    postedAdCompaigns.objects.create(
                                        user = request_user ,
                                        adcopy = ad_copy,
                                        posting_group = group,
                                        fb_account = fb,
                                        posted = True ,
                                    )
                            
                            # add 1 to the posting limits and sleep
                            posting_limits += 1
                            if len(groups_with_no_admin) > 0 :
                                time.sleep(wait_after_each_post)

                            
                            ad_copy.number_of_grouos_posted_in += posting_limits
                            ad_copy.save()

                            # adding the persontage to the class for real
                            progress.set_progress(old_persontage + persontage_to_add, 100)

                            # add the persentage here
                            old_persontage += persontage_to_add
                            
                        # if account is banded continue to the next fb
                        if fb.accountStatus == 'banded from posting':
                            continue


                    if len(groups_with_admin) > 0 :
                        for group in groups_with_admin:

                            # loop trough the groups that did not need admin approvment
                            if posting_limits  >= setting.post_per_time :
                                break

                            # check if this ad posted before in this groups
                            try :
                                this_ad_alredy_posted_in_this_group = postedAdCompaigns.objects.get(
                                    user=request_user, 
                                    adcopy = ad_copy , 
                                    posting_group = group
                                    )
                                continue
                            except:
                                pass

                            # open new window and get to the group link
                            driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')  
                            driver.get(f"{group.group_link}")
                            time.sleep(2)
                        
                            # this will work if group band the user
                            try:
                                driver.find_element_by_xpath('//*[@aria-label="Go to News Feed"]')
                                group.active = False
                                group.save()
                                continue
                            except:
                                banded_group = None

                            #  get the upload_img input 
                            upload_img = None
                            while upload_img is None :
                                try:
                                    upload_img = driver.find_element_by_xpath("//input[@type='file']")
                                except :
                                    upload_img = None
                            
                            # define some vars 
                            to_change_copyWrite = copyWriting.objects.filter(user=request_user, str_nich = group.group_nich)
                            to_change_pic = imageGalery.objects.filter(user=request_user, str_nich = group.group_nich)
                            used_copy_Write = random.choices(to_change_copyWrite)
                            used_copy_image = random.choices(to_change_pic)
                            code = generateCode()


                            # try to upload the image and in case image did not find in that path som move to the except
                            try:
                                # upload the image and sleep
                                upload_img.send_keys(used_copy_image[0].image)
                                time.sleep(10)

                                # get the posting button
                                posting = None
                                while posting == None:
                                    try : 
                                        posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                    except:
                                        posting = None
                                time.sleep(5)

                                # pass the dumy copy write and code
                                actions = ActionChains(driver)
                                for item in used_copy_Write[0].description:
                                    actions.send_keys(item)
                                actions.send_keys(' ')
                                for item in code:
                                    actions.send_keys(item)
                                actions.send_keys(' ')
                                actions.perform()
                                time.sleep(2)
                                
                                # post
                                posting.click()
                            except:
                                
                                # delete that path cause it is not working
                                used_copy_image.delete()
                                
                                # get the add post button and click it then sleep for a while
                                add_post_button = None
                                trys = 0
                                while add_post_button is None and trys < 30:
                                    try:
                                        add_post_button = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]
                                        /div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div[1]/div[1]/div/div/div/div[1]/div""")
                                    except :
                                        add_post_button = None
                                        time.sleep(2)
                                    trys += 1                     
                                add_post_button.click()
                                time.sleep(12)

                                # get the posting button
                                posting = None
                                while posting == None:
                                    try : 
                                        posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                    except:
                                        posting = None
                                time.sleep(5)
                                
                                # pass the dumy copy write and code
                                actions = ActionChains(driver)
                                for item in used_copy_Write[0].description:
                                    actions.send_keys(item)
                                actions.send_keys(' ')
                                for item in code:
                                    actions.send_keys(item)
                                actions.send_keys(' ')
                                actions.perform()
                                time.sleep(2)
                                
                                # post
                                posting.click()
                            
                            # if fb band fb account from posting
                            try : 
                                posting = None
                                limits = 0
                                while posting == None and limits < 9:
                                    try :
                                        posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                                        time.sleep(30)
                                        limits += 1
                                        posting = None
                                    except:
                                        posting = True
                                if posting == None:   
                                    fb.accountStatus = 'banded from posting'
                                    fb.save()
                                    break
                            except:
                                pass
                            
                            # looking for the 1st post author
                            post = None
                            trying_limit = 0
                            trys = 0
                            while post is None and trys < 60:
                                try:
                                    post = driver.find_element_by_xpath('//*[@aria-posinset="1"]')
                                    post_autor = post.find_element_by_tag_name('h2').text
                                    if fb.fullname not in post_autor and trying_limit < 12:
                                        time.sleep(5)
                                        post = None 
                                except:
                                    post = None
                                    time.sleep(1)
                                    trys += 1
                                trying_limit += 1

                            # if the post author is the fb owner
                            if fb.fullname in post_autor :

                                # change group posting permestion to False
                                group.posting_with_permestion = False
                                group.save()

                                # create postedAdCompaigns posted with code
                                the_compagn = postedAdCompaigns.objects.create(
                                    user = request_user ,
                                    adcopy = ad_copy,
                                    posting_group = group,
                                    fb_account = fb,
                                    posted = True ,
                                    code = code
                                )

                                # find the code that we use in that post so we can now to any adcopy related
                                post_text = post.text
                                pattern = "#[A-Z]+"
                                code = re.findall(pattern, post_text)

                                # get the ad copy the post related to
                                try:
                                    ad = postedAdCompaigns.objects.get(user = request_user, done=False, code=code[0])
                                except IndexError:
                                    continue
                                
                                # see if the group is privit or public bu finding share button
                                element = None
                                element_tries = 0
                                while element == None and element_tries <= 5:
                                    try:
                                        element = post.find_element_by_xpath('//*[@aria-label="Send this to friends or post it on your Timeline."]')
                                    except:
                                        element = None
                                        time.sleep(5)
                                        element_tries += 1

                                # if group is public
                                if element :
                                    
                                    # click share then send trough messanger 
                                    driver.execute_script("arguments[0].click();", element)
                                    time.sleep(2)
                                    send_in_messanger = None
                                    while send_in_messanger == None:
                                        try:
                                            send_in_messanger = post.find_element_by_xpath("""//*[@id="mount_0_0"]/div/
                                            div[1]/div[1]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/
                                            div/div/div[1]/div/div[3]/div""")
                                        except:
                                            send_in_messanger = None
                                    send_in_messanger.click()
                                    time.sleep(2)

                                    message_pop_up = None
                                    while message_pop_up is None:
                                        try:
                                            message_pop_up = driver.find_element_by_xpath('//*[@aria-label="Send in Messenger"]')
                                        except:
                                            message_pop_up = None

                                    # get the lick from lessanger pop up
                                    post_link = None
                                    while post_link is None:
                                        try:
                                            post_link = message_pop_up.find_element_by_xpath("""//*[@id="mount_0_0"]/div/
                                            div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div[3]
                                            /div[1]/div/div/div[1]/div[1]""")                    
                                        except:
                                            post_link = None

                                    # pass the lick to the posted campain and save
                                    the_compagn.post_link = post_link.text
                                    the_compagn.save()
                                    posting_limits += 1

                                    # adding the persontage to the class for real
                                    progress.set_progress(old_persontage + persontage_to_add, 100)

                                    # add the persentage here
                                    old_persontage += persontage_to_add
                                    
                                    # find the close button on the messanger pop up and click it
                                    element = None
                                    element_tries = 0
                                    while element == None and element_tries <= 5:
                                        try:
                                            element = post.find_element_by_xpath('//*[@aria-label="Close"]')
                                        except:
                                            element = None
                                            time.sleep(5)
                                            element_tries += 1
                                    driver.execute_script("arguments[0].click();", element)
                                    time.sleep(4)

                                # if the group is privit
                                else:
                                    try:

                                        # get the links from the post
                                        tries = 0
                                        post_links = None
                                        post_link_list = []
                                        while post_links == None and tries < 10:
                                            try:
                                                post_links = post.find_elements_by_tag_name('a')
                                                for i in post_links :
                                                    post_link_list.append(i.get_attribute("href"))
                                            except:
                                                post_links = None
                                                time.sleep(4)
                                                tries += 1

                                        # if the link has gm. so it a link will lead to the post link
                                        photo_link = None
                                        for j in post_link_list:
                                            if 'gm.' in j:
                                                photo_link = j 
                                                break

                                        # get the pure link post
                                        pattren = '[gm\.]([0-9]+)'
                                        link = re.findall(pattren, photo_link)
                                        full_link = group.group_link  + 'permalink/' + link[0]
                                        the_compagn.post_link = full_link
                                        the_compagn.posted = True
                                        the_compagn.save()

                                    # if we cant have the link 
                                    except:

                                        # creat posted ad compaign with no link
                                        the_compagn.posted = True
                                        the_compagn.save()

                                    posting_limits += 1

                                    # adding the persontage to the class for real
                                    progress.set_progress(old_persontage + persontage_to_add, 100)

                                    # add the persentage here
                                    old_persontage += persontage_to_add
                                
                                # we are stiil in the case the post is posted without admin as inexpacted
                                # start to edit it by getting the menu icon 
                                menu_icon = post.find_element_by_xpath('//*[@aria-label="Actions for this post"]')
                                menu_icon.click()
                                edite = None
                                while edite == None:
                                    try: 
                                        edite = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]
                                        /div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/div/div[2]""")
                                    except:
                                        edite = None
                                edite.click()

                                # get the edit form pop up
                                edit_form = None
                                while edit_form == None:
                                    try:
                                        edit_form = driver.find_element_by_tag_name('form')
                                    except:
                                        edit_form = None

                                # get the field 
                                field = None
                                while field == None:
                                    try:
                                        field = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]/
                                        div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/
                                        div[2]/div[1]/div[1]/div[1]/div/div/div/div/div/div/div/div""")
                                    except:
                                        field = None 

                                # get the save button  
                                save = None
                                while save == None:
                                    try:
                                        save = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/
                                        div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/
                                        div/div[1]/div[3]/div[2]/div/div""")
                                    except:
                                        save = None    

                                # get the x button that remove the pic if it exists
                                remove_pic = None
                                trying_limit = 0
                                while remove_pic == None and trying_limit < 50 :
                                    try:
                                        remove_pic = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]
                                        /div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/
                                        div[1]/div[2]/div[1]/div[2]/div/div[2]/div""")
                                    except:
                                        remove_pic = None 
                                        time.sleep(5)
                                        trying_limit += 1
                                
                                # remove pic if it is exists
                                time.sleep(10)
                                if remove_pic != None:
                                    remove_pic.click()
                                    time.sleep(3)
                                
                                # if ad copy has image
                                if ad_copy.image:
                                    # get the input file then put image url
                                    upload_img = None
                                    while upload_img == None:
                                        try:
                                            upload_img = driver.find_element_by_xpath("//div[@id='toolbarLabel']/following-sibling::div")
                                        except:
                                            upload_img = None
                                    upload_img_field = None
                                    while upload_img_field == None:
                                        try:
                                            upload_img_field = upload_img.find_element_by_tag_name("input")
                                        except:
                                            upload_img_field = None
                                    upload_img_field.send_keys(ad_copy.image)

                                # delete the dumy ad cop  
                                for i in range(len(field.text) + 1):
                                    field.send_keys(Keys.BACK_SPACE)
                                # add the real ad copy
                                for item in ad.adcopy.descriprtion:
                                    field.send_keys(item)
                                
                                # add the adcopy link
                                field.send_keys(' ')
                                for item in ad.adcopy.link:
                                    field.send_keys(item)

                                time.sleep(10)
                                save.click()
                                time.sleep(10)
                                
                                # this will work if fb account get banded from posting
                                try : 
                                    posting = None
                                    limits = 0
                                    while posting == None and limits < 9:
                                        try :
                                            posting = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div')
                                            time.sleep(30)
                                            limits += 1
                                            posting = None
                                        except:
                                            posting = True
                                    if posting == None:   
                                        fb.accountStatus = 'banded from posting'
                                        fb.save()
                                        break
                                except:
                                    pass

                                # sleep for a while then continue to next group                    
                                time.sleep(wait_after_each_post)
                                continue
                                
                            else:

                                # keep the posting_with_permestion as it is
                                group.posting_with_permestion = True
                                group.save()
                            
                            # continue as the group still have addmin permesion
                            # create postedAdCompaigns with the code and not posted
                            postedAdCompaigns.objects.create(
                                user = request_user ,
                                adcopy = ad_copy,
                                fb_account = fb,
                                posted = False,
                                posting_group = group,
                                code = code
                            )
                            posting_limits += 1

                            # sleep for a while
                            if len(groups_with_admin) > 0  :
                                time.sleep(wait_after_each_post)

                            # adding the persontage to the class for real
                            progress.set_progress(old_persontage + persontage_to_add, 100)

                            # add the persentage here
                            old_persontage += persontage_to_add

                            ad_copy.number_of_grouos_posted_in += posting_limits
                            ad_copy.save()

                        # if fb is banded continue to the next fb
                        if fb.accountStatus == 'banded from posting':
                            continue

                # if the fb have no groups move to the bext fb    
                else:
                    continue
                
                driver.close()

            # if the ad posted in all groups we will mark it as done
            len_of_all_groups_in_this_niche = len(myGroupsModel.objects.filter(user = request_user, group_nich = ad_copy.niche ))
            if ad_copy.number_of_grouos_posted_in >= len_of_all_groups_in_this_niche:
                ad_copy.used = True
                ad_copy.save()          
     
    # end the code

    return 'Done'


@shared_task(bind=True)
def checkPostedApprovedAndChangeItTask(self, pk):

    # get the request user
    request_user = User.objects.get(id = pk)

    # get user settings to get wait_after_each_post
    setting = settingModel2.objects.get(user = request_user)

    # time to wait after each post
    wait_after_each_post =  setting.to_wait_after_each_post * 60

    # this user active fb account
    fb_accounts = fbAccountsModel.objects.filter(user = request_user, accountStatus = 'active')

    # start the code
    to_remplace_with = postedAdCompaigns.objects.filter(user=request_user, posted=False, done=False)

    # while there is some posts that did not get approved for this user then 
    # loop trought his acccount looking for them
    while len(to_remplace_with) > 0:
        for fb in fb_accounts:
            # get the ad campaigns that posted with that fb and did not get approved yet
            to_remplace_with_for_this_fb = postedAdCompaigns.objects.filter(
                user=request_user, 
                posted=False, 
                done=False, 
                fb_account = fb
                )
            # if there is no ad campaigns that posted with that fb so sleep then move on
            if len(to_remplace_with_for_this_fb) == 0 :
                time.sleep(400)
                continue


            # get the driver
            driver = getDriver(fb)

            # check if the fb account get banded
            if 'https://www.facebook.com/checkpoint' in driver.current_url or 'https://www.facebook.com/checkpoint/?next' in driver.current_url:
                fb.accountStatus = 'Blocked'
                fb.save()   
                continue

            # check if fb account password change or wrong
            try:
                error_box = driver.find_element_by_id('error_box')
                fb.accountStatus = 'Unactive'
                fb.save()
                continue

            # make sure the fb account use the new version of fb
            except:
                driver.get('https://www.facebook.com/me/')
                time.sleep(1)
                try:
                    old_facebook_version = driver.find_element_by_tag_name('h1').text
                    if old_facebook_version == 'facebook' or old_facebook_version == 'فيسبوك' :
                        fb.accountStatus = 'Old fb version'
                        fb.save()
                        continue
                except:
                    pass

            # go to notification
            driver.get('https://www.facebook.com/notifications')

            # scroll down and get all notifs in a list
            my_notifs = []
            def scroll():
                while len(my_notifs) == 0:
                    for i in range(5):
                        try : 
                            notification_bar = driver.find_elements_by_xpath('//*[@aria-label="Notifications"]/div/div/div/div')
                            for notif in notification_bar:
                                driver.execute_script("arguments[0].scrollIntoView();", notif)
                                time.sleep(0.05)
                                if notif not in my_notifs:
                                    my_notifs.append(notif)
                        except :
                            pass
            scroll()

            # get the notifs that mark to a post or photo aprrovment in a new list
            post_approved_notification = []
            for notification in my_notifs:
                try :
                    if 'An admin approved your post in' in  notification.text or 'An admin approved your photo in' in  notification.text:
                        link = None
                        while link == None:
                            try:
                                link =  notification.find_element_by_tag_name('a')
                                url = link.get_attribute("href")
                                post_approved_notification.append(url)
                            except:
                                link = None
                except:
                    continue
            
            # loop trought post_approved_notification
            for notification in post_approved_notification :
                
                # get the post
                driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')  
                driver.get(notification)
                time.sleep(2)
                post = None
                trys = 0
                while post is None and trys < 60:
                    try:
                        post = driver.find_element_by_xpath('//*[@aria-posinset="1"]')
                    except:
                        post = None
                        time.sleep(1)
                        trys += 1

                # get the code 
                post_text = post.text
                pattern = "#[A-Z]+"
                code = re.findall(pattern, post_text)
                try:
                    # search for adcampain that mach the code 
                    ad = postedAdCompaigns.objects.get(user = request_user, posted=False, done=False, code=code[0])

                except :

                    # if we did not find adcampain that mach it so move on
                    continue

                # get the menu icon and click it
                menu = driver.find_element_by_xpath('//*[@aria-label="Actions for this post"]')
                menu.click()

                # get the edit button and click it
                edite = None
                while edite == None:
                    try:
                        edite = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/
                        div[1]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/div/div[2]""")
                    except:
                        edite = None
                edite.click()

                # get the field for writing
                field = None
                while field == None:
                    try: 
                        field = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/
                        div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[2]/div[1]/div[1]
                        /div[1]/div/div/div/div/div/div/div/div""")
                    except:
                        field = None    

                # get the save button 
                save = None
                while save == None:
                    try:
                        save = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/
                        div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div""")
                    except:
                        save = None    

                # get the remove pic icon if exests
                remove_pic = None
                trying_limit = 0
                while remove_pic == None and trying_limit < 40 :
                    try:
                        remove_pic = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]
                        /div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[2]/div[1]/div[2]
                        /div/div[2]/div""" )
                    except:
                        remove_pic = None 
                        trying_limit += 1

                # if pic exists remove it
                if remove_pic != None:
                    remove_pic.click()
                    time.sleep(3)
                
                # delete the dummy copy write
                for i in range(len(field.text) + 1):
                    field.send_keys(Keys.BACK_SPACE)

                # pass the real adcopy copywrite
                for item in ad.adcopy.descriprtion:
                    field.send_keys(item)

                # space
                field.send_keys(' ')

                # pass the adcopy link
                for item in ad.adcopy.link:
                    field.send_keys(item)
                
                time.sleep(10)

                if ad.adcopy.image:
                    # try to add image by link and if something went wrong with the image path just pass
                    try : 
                        # if the adcopy has image so upload it if it not has it it will pass this block of code
                        # if ad copy has image
                        if ad_copy.image:
                            # get the input file then put image url
                            upload_img = None
                            while upload_img == None:
                                try:
                                    upload_img = driver.find_element_by_xpath("//div[@id='toolbarLabel']/following-sibling::div")
                                except:
                                    upload_img = None
                            upload_img_field = None
                            while upload_img_field == None:
                                try:
                                    upload_img_field = upload_img.find_element_by_tag_name("input")
                                except:
                                    upload_img_field = None
                            upload_img_field.send_keys(ad.adcopy.image)
                    except:
                        pass
                    
                # save the changes    
                save.click()

                # sleep
                time.sleep(wait_after_each_post)
                
                
                # this will work if fb account get banded from posting
                try : 
                    posting = None
                    limits = 0
                    while posting == None and limits < 9:
                        try :
                            posting = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div')
                            time.sleep(30)
                            limits += 1
                            posting = None
                        except:
                            posting = True
                    if posting == None:   
                        fb.accountStatus = 'banded from posting'
                        fb.save()
                        break
                except:
                    pass

                # get the post link and save it
                pattern = "^([^?]*)"
                link = re.findall(pattern, driver.current_url )
                ad.post_link = link[0]
                ad.posted = True
                ad.save()

            # close the driver between the changing of accounts
            driver.close()

            # sleep between the changing of accounts
            time.sleep(400)

        # sleep after each tour 
        time.sleep(400)
            
    return 'Done'