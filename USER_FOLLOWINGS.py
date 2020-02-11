# 1.) This program is using firefox, so for your specific browser you need to download the respective geckodriver for selenium to work
# 2.) This program utilizes the facebook login and not the twitter login
# 3.) This program reads in a csv file that already has usernames collected from a previous scraping (usernames will be concatonated with the curious cat url to visit user profile)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import csv
import pandas as pd
import re

def is_valid_user(driver):
    try:
        driver.find_element_by_class_name('error')
        return False
    except NoSuchElementException:
        return True

#opening raw browser
browser = webdriver.Firefox()
sleep(2)

#telling browser to go to curious cat and saves the main browser window for later use
browser.get('https://curiouscat.me/')
parent_h = browser.current_window_handle

#finds and clicks "already have an account"
ALREADY_HAVE_AN_ACCOUNT = browser.find_element_by_class_name('already')
ALREADY_HAVE_AN_ACCOUNT.click()

#A Modal window is displayed after clicking login, so setting a wait until the modal is fully loaded, then clicks login with facebook
FACEBOOK_BUTTON = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/main/div/div/div[5]/div[4]/div/div/div/div/p[2]/a')))
FACEBOOK_BUTTON.click()


#switching to pop up windows which is generated for the login
signin_window_handle = None
while not signin_window_handle:
    for handle in browser.window_handles:
        if handle != parent_h:
            signin_window_handle = handle
            break
browser.switch_to_window(signin_window_handle)


#waits until login button is clickable, then the fields will be ready to accept the keys
LOGIN = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="loginbutton"]')))

#sends your username and password
browser.find_element_by_id("email").send_keys('') # INPUT YOUR EMAIL USED FOR FACEBOOK
browser.find_element_by_id("pass").send_keys('') # INPUT YOUR FACEBOOK PASSWORD
browser.find_element_by_id("loginbutton").click()

#switching back to main browser
browser.switch_to_window(parent_h)
sleep(5)

#####################################################################################################################################################################
users_already_collected = set() # original set will contain users that were read in from csv
user_no_followings = set() # users that do not have followers
user_deactivated = set() # user profiles that are deactivated
user_no_stats = set()
visit_users = set() # users we are going to visit

#row = ['user','followings']
#with open('curiouscat_user_followings.csv','w') as f:
#    thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
#    thewriter.writerow(row)

#row = ['user']
#with open('curiouscat_no_followings.csv','w') as f:
#    thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
#    thewriter.writerow(row)

# read in the users that have been successfully collected
df = pd.read_csv('users_followings.csv')
column_of_users_followings = df['user'].values

for user in column_of_users_followings:
    users_already_collected.add(str(user))

# read in csv that contains the users with no followers
df = pd.read_csv('users_no_followings.csv')
column_of_no_followings = df['user'].values

for user in column_of_no_followings:
    user_no_followings.add(str(user))

#read in deactivated users
df = pd.read_csv('users_deactivated.csv')
column_of_deactivated_users = df['user'].values

for user in column_of_deactivated_users:
    user_deactivated.add(str(user))

#read in users with no stats
df = pd.read_csv('users_no_stats.csv')
column_of_no_stat_users = df['user'].values

for user in column_of_no_stat_users:
    user_no_stats.add(str(user))

url = 'https://curiouscat.me/'

# reads in users from main csv
df = pd.read_csv('users_collected.csv')
column_of_mass_users = df['user'].values

# adds users read in from main csv as long as they have not already been visited
for user in column_of_mass_users:
    if user not in users_already_collected and user not in user_no_followings and user not in user_deactivated and user not in user_no_stats:
        visit_users.add(str(url+user))

print('number of users read in from followings csv: ' + str(len(users_already_collected)))
print('number of users read in from no followings csv: ' + str(len(user_no_followings)))
print('number of users read in from deactivated user csv: ' + str(len(user_deactivated)))
print('number of users read in from missing stats csv: ' + str(len(user_no_stats)))
print('number of visits left: ' + str(len(visit_users)))
number_of_visits_left = len(visit_users)
########################################################################################################################################################################
visit_users = list(visit_users)

for user in visit_users:

    try:
        browser.get(user)
    except TimeoutException:
        browser.refresh()
    sleep(3)

    if not is_valid_user(browser):
        print('This user has been deactivated')
        row = [user[22:]]
        with open('users_deactivated.csv','a') as f:
            thewriter = csv.writer(f,delimiter = ',', quoting=csv.QUOTE_MINIMAL)
            thewriter.writerow(row)
        continue

    try:
        stats = WebDriverWait(browser,20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[4]/div[3]")))
    except TimeoutException as ex:
        print('This user does not have their stats posted')
        row = [user[22:]]
        with open('users_no_stats.csv','a') as f:
            thewriter = csv.writer(f,delimiter = ',', quoting=csv.QUOTE_MINIMAL)
            thewriter.writerow(row)
        continue

    numberOfFollowings = stats.find_element_by_xpath("/html/body/div[1]/div[1]/div[4]/div[3]/div[3]/span[2]").text
    
    if 'k' in numberOfFollowings:
        numberOfFollowings = numberOfFollowings.replace("k","")
        numberOfFollowings = numberOfFollowings.replace(".","")


    if 'K' in numberOfFollowings:
        numberOfFollowings = numberOfFollowings.replace("K","")
        numberOfFollowings = numberOfFollowings.replace(".","")

    if int(numberOfFollowings) == 0:
        print('This user has no followings')
        row = [user[22:]]
        with open('users_no_followings.csv','a') as f:
            thewriter = csv.writer(f,delimiter = ',', quoting=csv.QUOTE_MINIMAL)
            thewriter.writerow(row)
        continue

    if int(numberOfFollowings) > 0:
        print("This user has some followings")

        FOLLOWINGS_BUTTON = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[1]/div[4]/div[3]/div[3]')))
        FOLLOWINGS_BUTTON.click()
        sleep(7)

        CardContainer = WebDriverWait(browser,20).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div[1]/div[5]/div[4]/div/div/div[2]/div")))
        followingCards = CardContainer.find_elements_by_xpath(".//div[@class='user-preview-card card']")

        for card in followingCards:
            #numberOfAnswers = card.find_element_by_xpath(".//p[@class='answers']").text
            #numberOfAnswers = int(re.search(r'\d+',numberOfAnswers).group())
            following_href = card.find_element_by_xpath(".//a[@class='userlink']").get_attribute("href")[22:]
            #if user_href not in usr_href_original_set and user_href not in usr_href_original:
            row = [user[22:],following_href]
            with open('users_followings.csv','a') as f:
                thewriter = csv.writer(f,delimiter = ',', quoting=csv.QUOTE_MINIMAL)
                thewriter.writerow(row)

    print("User " + str(user) + " has " + str(numberOfFollowings) + " followings")

print('Collection complete.')
