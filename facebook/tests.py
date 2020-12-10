from django.test import TestCase
from selenium import webdriver
import time
from selenium.common.exceptions import (
    NoSuchWindowException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    WebDriverException,
    )
from selenium.webdriver.common.keys import Keys

# Create your tests here.


def test1():
    # get the request user

    # this user active fb account
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('headless')
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = None
    try:
        driver = webdriver.Chrome('facebook/static/facebook/chrom/chromedriver', chrome_options=chrome_options)
        driver.get('https://www.facebook.com')
    except WebDriverException:
         try:
            driver = webdriver.Chrome('facebook/static/facebook/chrom/chromedriver1', chrome_options=chrome_options)
            driver.get('https://www.facebook.com')
         except WebDriverException:
            try:
                driver = webdriver.Chrome('facebook/static/facebook/chrom/chromedriver2', chrome_options=chrome_options)
                driver.get('https://www.facebook.com')
            except WebDriverException:
                return redirect('dashboard:dashboard')
    email = driver.find_element_by_id('email')
    fb_password = driver.find_element_by_id('pass')
    time.sleep(5)
    for item in 'nor2.imqi@gmail.com':
        email.send_keys(item)
    time.sleep(1)
    for item in '15719211+':
        fb_password.send_keys(item)
    time.sleep(3)
    fb_password.send_keys(Keys.RETURN)
    time.sleep(1)

    driver.get('https://www.facebook.com/groups/3532632766761524')
    invite = None
    while invite == None :
        # we loop to give 5 chances to find invit butoon
        try:
            invite = driver.find_element_by_xpath('//*[@aria-label="Invite"]')
        except :
            invite = None
            print('no invite')

    print(f'invite: {invite}')

test1()