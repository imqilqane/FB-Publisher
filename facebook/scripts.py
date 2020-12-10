from django.shortcuts import render, redirect
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from requests.compat import quote_plus
from selenium.common.exceptions import (
    NoSuchWindowException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    WebDriverException,
    )
import time, random, string, os

def generateCode():
    alphs = list(string.ascii_uppercase)
    code = '#'
    for i in range(7):
        code += random.choice(alphs)
    return code


def getDriver(fb):
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
    for item in fb.username:
        email.send_keys(item)
    time.sleep(1)
    for item in fb.password:
        fb_password.send_keys(item)
    time.sleep(3)
    fb_password.send_keys(Keys.RETURN)
    time.sleep(1)

    return driver

