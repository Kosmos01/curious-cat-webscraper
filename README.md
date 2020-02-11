# curious-cat-webscraper
Webscraper I designed to collect user posts and descriptive metadata from the anonymous QA site CuriousCat.


(1) CC_COLLECT.py
      main file to go and collect all of the posts on a users' profile and descriptive metadata. Checks if user profile is
      deactivated, if they have any posts on their profile, if the user has already been visited, and if the user 
      profile is primarily english.
      
(2) USER_FOLLOWERS.py
      Collects the username of those who are followers of the main users scraped during CC_COLLECT.py. Checks if users
      have any followers and if the user even has this information public (user can hide their followers/followings)
   
(3) USER FOLLOWINGS.py
      Similar to USER_FOLLOWERS.py, but collects the username of followings. 
