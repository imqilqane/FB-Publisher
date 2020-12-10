for fb in fb_accounts:
    posting_limits = 0
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
    if posting_limits > setting.post_per_time :
        break
    print('debug')
    user_groups = myGroupsModel.objects.filter(user = request_user, facebook_account = fb, approved = True, )
    user_groups_len = len(user_groups)

    # if the fb have groups more than 0
    if user_groups_len > 0:
        groups_with_no_admin = myGroupsModel.objects.filter(
            user = request_user,
            facebook_account = fb,
            approved = True, 
            active = True,
            group_nich = ad_copy.niche,
            posting_with_permestion = False,
            )
        groups_with_admin = myGroupsModel.objects.filter(
            user = request_user,
            facebook_account = fb,
            approved = True, 
            active = True,
            group_nich = ad_copy.niche,
            posting_with_permestion = True,
            )
        print('debug 1')
        if len(groups_with_no_admin) > 0:

            # loop trough the groups that did not need admin approvment
            for group in groups_with_no_admin:
                
                # if we pass the posting limits we will break the loop to pass to the biggest loop
                if posting_limits  > setting.post_per_time :
                    break
                
                # check if this ad posted before in this groups
                try :
                    this_ad_alredy_posted_in_this_group = postedAdCompaigns.objects.get(
                        user=request_user, 
                        adcopy = ad_copy , 
                        posting_group = group
                        )
                    print('this_ad_alredy_posted_in_this_group')
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
                    print('group band the user')
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
                            print('none 651')
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
                            print('none')  

                    # define punsh of vars  
                    to_change_copyWrite = copyWriting.objects.filter(user=request_user, str_nich = group.group_nich)
                    to_change_pic = imageGalery.objects.filter(user=request_user, str_nich = group.group_nich)
                    used_copy_Write = random.choices(to_change_copyWrite)
                    used_copy_image = random.choices(to_change_pic)
                    code = generateCode()

                    # upload the image and sleep
                    upload_img.send_keys(used_copy_image[0].image.path)
                    time.sleep(10)

                    # get the posting button
                    posting = None
                    while posting == None:
                        try : 
                            posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                        except:
                            posting = None
                            print('none 909')
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
                            print('post did not banded')
                    if posting == None:   
                        fb.accountStatus = 'banded from posting'
                        fb.save()
                        break
                except:
                    pass
                

                # looking 1st post author
                post = None
                trying_limit = 0
                print('looking for post author')
                while post is None :
                    try:
                        post = driver.find_element_by_xpath('//*[@aria-posinset="1"]')
                        post_autor = post.find_element_by_tag_name('h2').text
                        if fb.fullname not in post_autor and trying_limit < 12:
                            time.sleep(5)
                            post = None 
                            print('post author is not fb account')
                            print('post author', post_autor)
                            print('fb.fullname', fb.fullname)
                    except:
                        post = None
                        print('none 735')
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
                    print('creat compaign for this ad copy 744')
                    postedAdCompaigns.objects.create(
                        user = request_user ,
                        adcopy = ad_copy,
                        posting_group = group,
                        fb_account = fb,
                    )
                    print('wait_after_each_post :',wait_after_each_post)
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
                        print('none 763')
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
                            send_in_messanger = post.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div[1]/div/div[3]/div')
                        except:
                            send_in_messanger = None
                            print('None 776')
                    send_in_messanger.click()
                    time.sleep(2)
                    message_pop_up = None
                    while message_pop_up is None:
                        try:
                            message_pop_up = driver.find_element_by_xpath('//*[@aria-label="Send in Messenger"]')
                        except:
                            message_pop_up = None
                            print('None 4')
                    
                    # get the post link and creat the postedAdCompaigns
                    post_link = None
                    while post_link is None:
                        try:
                            post_link = message_pop_up.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]')                    
                        except:
                            post_link = None
                            print('None 793'
                    print('creat compaign for this ad copy 795')
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
                    try
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
                        print(f'full_link {full_link}'
                        print('creat compaign for this ad copy 830')
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
                        print('creat posted ad compaign with no link 840')
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
                    print(f'wait for {wait_after_each_post} seconds')
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
                if posting_limits  > setting.post_per_time :
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
                    banded_group = Non

                #  get the upload_img input 
                upload_img = None
                while upload_img is None :
                    try:
                        upload_img = driver.find_element_by_xpath("//input[@type='file']")
                    except :
                        upload_img = None
                        print('none')  
                 
                # define some vars
                to_change_copyWrite = copyWriting.objects.filter(user=request_user, str_nich = group.group_nich)
                to_change_pic = imageGalery.objects.filter(user=request_user, str_nich = group.group_nich)
                used_copy_Write = random.choices(to_change_copyWrite)
                used_copy_image = random.choices(to_change_pic)
                code = generateCode()

                # upload the image and sleep
                upload_img.send_keys(used_copy_image[0].image.path)
                time.sleep(10)

                # get posting button
                posting = None
                while posting == None:
                    try : 
                        posting = driver.find_element_by_xpath('//*[@aria-label="Post"]')
                    except:
                        posting = None
                        print('none 909')
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
                            print('post did not banded')
                    if posting == None:   
                        fb.accountStatus = 'banded from posting'
                        fb.save()
                        break
                except:
                    pass
                
                # looking for the 1st post author
                post = None
                trying_limit = 0
                print('looking for post author')
                while post is None :
                    try:
                        post = driver.find_element_by_xpath('//*[@aria-posinset="1"]')
                        post_autor = post.find_element_by_tag_name('h2').text
                        if fb.fullname not in post_autor and trying_limit < 12:
                            time.sleep(5)
                            post = None 
                            print('post author is not fb account')
                    except:
                        post = None
                        print('none 956')
                    trying_limit += 1

                # if the post author is the fb owner
                if fb.fullname in post_autor :

                    # change group posting permestion to False
                    group.posting_with_permestion = False
                    group.save()

                    # create postedAdCompaigns posted with code
                    print('creat compaign for this ad copy 962')
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
                            print('none 987')
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
                                send_in_messanger = post.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div[1]/div/div[3]/div')
                            except:
                                send_in_messanger = None
                                print('None 999')
                        send_in_messanger.click()
                        time.sleep(2)

                        message_pop_up = None
                        while message_pop_up is None:
                            try:
                                message_pop_up = driver.find_element_by_xpath('//*[@aria-label="Send in Messenger"]')
                            except:
                                message_pop_up = None
                                print('None 1008')

                        # get the lick from lessanger pop up
                        post_link = None
                        while post_link is None:
                            try:
                                post_link = message_pop_up.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]')                    
                            except:
                                post_link = None
                                print('None 1015')

                        # pass the lick to the posted campain and save
                        the_compagn.post_link = post_link.text
                        the_compagn.save()
                        posting_limits += 

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
                                print('none 1032')
                                time.sleep(5)
                                element_tries += 1
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(4)

                    # if the group is privit
                    else:
                        try:

                            # get the links from the post
                            print('creat posted ad compaign with link 1038')
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
                            print(f'full_link {full_link}')
                            the_compagn.post_link = full_link
                            the_compagn.posted = True
                            the_compagn.save()

                        # if we cant have the link 
                        except:

                            # creat posted ad compaign with no link
                            print('creat posted ad compaign with no link')
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
                            edite = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]/div/div[2]')
                        except:
                            edite = None
                            print("edite")      
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
                            field = driver.find_element_by_xpath("""//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]
                                    /div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div/div/div/div/div/div""")
                        except:
                            field = None 
                            print('none 1098')   

                    # get the save button  
                    save = None
                    while save == None:
                        try:
                            save = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div')
                        except:
                            save = None    
                            print('none') 

                    # get the x button that remove the pic if it exists
                    remove_pic = None
                    trying_limit = 0
                    while remove_pic == None and trying_limit < 50 :
                        try:
                            remove_pic = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div[1]/div[2]/div[1]/div[2]/div/div[2]/div')
                        except:
                            remove_pic = None 
                            time.sleep(5)
                            print('none 1114', trying_limit)
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
                                print(' none upload_img ')
                        upload_img_field = None
                        while upload_img_field == None:
                            try:
                                upload_img_field = upload_img.find_element_by_tag_name("input")
                            except:
                                upload_img_field = None
                                print(' none upload_img_field '
                        upload_img_field.send_keys(ad_copy.image.path)

                    # delete the dumy ad cop  
                    for i in range(len(field.text) + 1):
                        field.send_keys(Keys.BACK_SPACE
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
                                print('post did not banded')
                        if posting == None:   
                            fb.accountStatus = 'banded from posting'
                            fb.save()
                            break
                    except:
                        pass

                    # sleep for a while then continue to next group                    
                    print(f'wating for {wait_after_each_post}')
                    time.sleep(wait_after_each_post)
                    continue
                    
                else:

                    # keep the posting_with_permestion as it is
                    group.posting_with_permestion = True
                    group.save()
                
                # continue as the group still have addmin permesion
                # create postedAdCompaigns with the code and not posted
                print('creat compaign for this ad copy 1174')
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
                    print(f'wait for {wait_after_each_post} seconds')
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
