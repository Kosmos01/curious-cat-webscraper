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
from nltk.tokenize import word_tokenize
import pandas as pd
from nltk.corpus import words

set_of_words = set(words.words())

def trim (text):
    text = text.replace('\n','').replace(',','').replace(';','').replace('-','').replace('|','').replace('"','').replace("'","")
    return text

def is_valid_user(driver):
    try:
        driver.find_element_by_class_name('error')
        return False
    except NoSuchElementException:
        return True

def count_en(post):
    tot = 0
    eng = 0
    tokens = word_tokenize(post) # tokenizing post
    words_to_check = [word for word in tokens if word.isalpha()] # removing punctuation
    #stop_words = set(stopwords.words('english')) 
    #words = [w for w in words if not w in stop_words] #removing stop words
    for word in words_to_check:
        tot += 1
        if word.lower() in set_of_words:
            eng += 1
    return tot, eng

def user_has_posts(driver):
    try:
        driver.find_element_by_class_name('no-posts')
        return False
    except NoSuchElementException:
        return True

def is_user_using_english(post):
        tot, en = count_en(post)

        if tot != 0:
            en_percent = en * 1.0 / tot
            if en_percent > 0.5:
                return True
            else:
                return False
        else:
            return False

def get_poster(post):
    found = False

    try:
        poster = post.find_element_by_xpath(".//a[@class='username']").text
        found = True
    except NoSuchElementException:
        print('The posters name is not here.')

    if found:
        return poster

    try:
        poster = post.find_element_by_xpath(".//a[@class='username router-link-exact-active router-link-active']")
        return poster
    except NoSuchElementException:
        print('This should not output')


def is_profile_english(browser):
    print("Checking if the user is using at least 45% english in all of their posts...")
    answer_question_pair_count = 0

    total_first_page_posts = 0

    profile = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.profile')))

    posts = profile.find_elements_by_class_name('post')

    for post in posts:

        total_first_page_posts+=1
        # grabs question in the current post
        question = post.find_element_by_xpath(".//div[@class='question-text isInProfile']").text

        # checks if post is primarily english
        if not is_user_using_english(question):
            del question
            continue

        # grabs answer in the current post
        answer = post.find_element_by_xpath(".//div[@class='reply-text']").text

        if not is_user_using_english(answer):
            del answer
            del question
            continue

        answer_question_pair_count+=1

    percentage = answer_question_pair_count * 1.0 / total_first_page_posts
    print("the percentage is: " + str(percentage))

    if percentage > .45:
        print("proceeding to load the rest of the posts...")
        return True
    else:
        print("Not enough english on the first page...")
        return False

#opening raw browser
browser = webdriver.Firefox()
sleep(2)
browser.set_window_size(1000,1000) # maxing out browser window

#telling browser to go to curious cat and saves the main browser window for later use
browser.get('https://curiouscat.me/')
parent_h = browser.current_window_handle

#finds and clicks "already have an account"
ALREADY_HAVE_AN_ACCOUNT = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.already')))
#ALREADY_HAVE_AN_ACCOUNT = browser.find_element_by_class_name('already')
ALREADY_HAVE_AN_ACCOUNT.click()

#A Modal window is displayed after clicking login, so setting a wait until the modal is fully loaded, then clicks login with facebook
#FACEBOOK_BUTTON = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/main/div/div/div[5]/div[2]/div/div/div/div/p[2]/a')))
FACEBOOK_BUTTON = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.btn-facebook')))
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
LOGIN = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#loginbutton')))

#sends your username and password
browser.find_element_by_id("email").send_keys('') # INPUT YOUR EMAIL USED FOR FACEBOOK !!!!!!!
browser.find_element_by_id("pass").send_keys('') # INPUT YOUR FACEBOOK PASSWORD !!!!!!!
browser.find_element_by_id("loginbutton").click()

#switching back to main browser
browser.switch_to_window(parent_h)
sleep(5)

#####################################################################################################################################################################
followers_set = set() # 
followings_set = set() # users that have no stats
user_set = set() # users to be collected
collected_set = set()
collect_set = set()

deleted_set = set()
not_enough_english = set()
no_posts = set()

problem_user_set = set()

deleted_csv = pd.read_csv('users_deactivated.csv')
deleted_df = deleted_csv['user'].values

not_english_csv = pd.read_csv('users_no_english.csv')
not_english_df = not_english_csv['user'].values

no_posts_csv = pd.read_csv('users_no_posts.csv')
no_posts_df = no_posts_csv['user'].values

# both grab raw usernames
user_csv = pd.read_csv('users_sexual.csv')
user_df = user_csv['user'].values

collected_csv = pd.read_csv('users_collected.csv')
collected_df = collected_csv['user'].values

followers_csv = pd.read_csv('curiouscat_user_followers.csv')
followers_df = followers_csv[['user','followers']].values

followings_csv = pd.read_csv('curiouscat_user_followings.csv')
followings_df = followings_csv[['user','followings']].values


for user in deleted_df:
    problem_user_set.add(user)

for user in not_english_df:
    problem_user_set.add(user)

for user in no_posts_df:
    problem_user_set.add(user)

# appends the username to the curious cat url so that the browser can go to their profile
for user in collected_df:
    collected_set.add(user)

for user in user_df:
    user_set.add(user)

for pair in followers_df:
    if pair[0] in user_set and pair[1] not in collected_set and pair[1] not in problem_user_set:
        collect_set.add(pair[1])

for pair in followings_df:
    if pair[0] in user_set and pair[1] not in collected_set and pair[1] not in problem_user_set:
        collect_set.add(pair[1])

#with open('collected_CB_users.csv','w') as f:
#        thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
#        row = ['user','answer','question','poster','post_id','time']
#        thewriter.writerow(row)

""" with open('CB_users_deactivated.csv','w') as f:
        thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
        row = ['user']
        thewriter.writerow(row)

with open('CB_users_no_posts.csv','w') as f:
        thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
        row = ['user']
        thewriter.writerow(row)

with open('not_english.csv','w') as f:
    thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
    row = ['user']
    thewriter.writerow(row) """
########################################################################################################################################################################
#converting set to list for iteration
collect_list = list(collect_set)
deleted_list = []
no_posts_list = []
not_english = []
print("users to be collected is: " + str(collect_list))
print("number of users to collect: " + str(len(collect_list)))
url = "https://curiouscat.me/"

retry = False
# for loop to go to each user profile
for j in collect_list:
    try:
        browser.get(str(url+j))
    except TimeoutException:
            browser.refresh()
        
    sleep(3)

    # skips over user profiles who are deactivated
    if not is_valid_user(browser):
        print('not valid user')
        with open('users_deactivated.csv','a') as f:
            thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
            row = [j]
            thewriter.writerow(row)
        continue

    if not user_has_posts(browser):
        print('user has no posts')
        with open('users_no_posts.csv','a') as f:
           thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
           row = [j]
           thewriter.writerow(row)
        continue
    
    if not is_profile_english(browser):
        print("The profile is not primaryily english...")
        with open('users_no_english.csv','a') as f:
           thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
           row = [j]
           thewriter.writerow(row)
        continue

    # grabs initial height of the page
    last_height = browser.execute_script("return document.body.scrollHeight")

    # while loop to keep scrolling down the page until all posts are loaded
    while True:
        print('loading more pages...')

        #Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #Wait to load page
        sleep(3)

        #Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        else:
            last_height = new_height

    # checks if the profile is primarily english
    if not is_profile_english(browser):
        not_english.append(j)
        print("The profile is not primaryily english...")
        continue

    # grabs profile where posts are located
    profile = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/div/div')))

    # grabs header so that we can grab the username
    header = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]')))

    # grabbing all posts in the user profile
    posts = profile.find_elements_by_class_name('post')

    # grabbing username
    username = j

    #goes to each post in the container that has all the posts
    for post in posts:

        # grabs question in the current post
        question = post.find_element_by_xpath(".//div[@class='question-text isInProfile']").text
        # checks if post is primarily english
        if not is_user_using_english(question):
            del question
            continue

        #trims question
        question = trim(question)

        # grabs answer in the current post
        answer = post.find_element_by_xpath(".//div[@class='reply-text']").text

        if not is_user_using_english(answer):
            del answer
            del question
            continue

        answer = trim(answer)

        # poster can be anon, another user, or the user themself. so this returns whichever is present.
        poster = get_poster(post)

        # grabs time of post
        time = post.find_element_by_xpath(".//a[@class='ago']").text

        # grabs post id
        post_id = post.find_element_by_xpath(".//a[@class='ago']").get_attribute("href")[-9:]

        # formatting row to write to file
        row = [username, answer, question, poster, post_id, time]
        print(row)

        # writing each post to file
        with open('users_collected.csv','a') as f:
            thewriter = csv.writer(f,delimiter = ',', quoting=csv.QUOTE_MINIMAL)
            thewriter.writerow(row)




#print("The number of deleted users are " + str(len(deleted_list)))
#print(deleted_list)

# if there is an inactive user this will write their username to another csv file
#if len(deleted_list) != 0:
#    for user in deleted_list: 
#        with open('CB_users_deactivated.csv','a') as f:
#            thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
#            thewriter.writerow(user)

#if len(no_posts_list) != 0:
#    for user in no_posts_list:
#         with open('CB_users_no_posts.csv','a') as f:
#            thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
#            thewriter.writerow(user)

#if len(not_english) != 0:
#    for user in not_english:
#         with open('not_english.csv','a') as f:
#            thewriter = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
#            thewriter.writerow(user)
