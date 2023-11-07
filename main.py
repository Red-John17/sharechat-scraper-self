#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import chromedriver_autoinstaller
import json
from constants import tag_urls, perTagLimit, outputName


# In[ ]:


# URL of the ShareChat page
url = "https://sharechat.com/trending/Hindi"
chromedriver_autoinstaller.install()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-popup-blocking')
driver = webdriver.Chrome(options=chrome_options)

# tag_url = "https://sharechat.com/tag/G7qd0K"

driver.get(url)
time.sleep(2)
post_done = set()
if os.path.exists(outputName):
    # read 
    with open(outputName, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            post_done.add(data['post_ph'])

outputJsonL = open(outputName, 'a', encoding='utf-8')
keepRunning = True

while keepRunning:
    for tag_url in tag_urls:
        postsDone = 0
        driver.get(tag_url)
        time.sleep(5)

        scroller = driver.find_element(By.XPATH,
                                    "//div[@class='infinite-list-wrapper']")
        newPosts = False
        posts = scroller.find_elements(
            By.XPATH, './/div[@data-cy="image-post"] | //div[@data-cy="video-post"] | //div[@data-cy="gif-post"]')

        for post in posts:
            try:
                # get the data-post-ph attribute of post
                post_ph = post.get_attribute('data-post-ph')
                if post_ph in post_done:
                    print("Post already done:", post_ph)
                    continue

                newPosts = True

                print("Post PH:", post_ph)

                post_done.add(post_ph)
                # Locate the elements containing the information
                author_element = post.find_element(
                    By.CSS_SELECTOR, 'strong[data-cy="author-name"]')
                author_name = author_element.text

                author_link_element = post.find_element(
                    By.CSS_SELECTOR, 'a[data-cy="avatar-tag"]')
                
                author_link = author_link_element.get_attribute('href')

                authorID = author_link[author_link.find('/profile/') +
                        len('/profile/'):author_link.find('?referer=')]

                topDetailsDiv = post.find_element(
                    By.XPATH, './/div[@class="H(100%) Pstart($xs) Fxg(1) Miw(0)"]')

                # find direct div inside it
                topDetailsDiv = topDetailsDiv.find_element(
                    By.XPATH, './div[@class="H(100%) Ta(start) D(f) Jc(c) Ai(fs) Fxd(c)"]')

                # direct divs inside it
                innerDivs = topDetailsDiv.find_elements(
                    By.XPATH, './div')
                text = innerDivs[1].text.split('•')
                years_before = text[1].strip()
                number_of_views = text[0].strip()

                post_caption = post.find_element(
                    By.XPATH, './/div[@data-cy="post-caption"]')
                pcText = post_caption.text

                print("Author Name:", author_name)
                print("Author Link:", author_link)
                print("Author ID:", authorID)
                print("Number of Views:", number_of_views)
                print("Years Before:", years_before)
                print("Post Caption:", pcText)

                # open new page comments
                commentLink = f"https://sharechat.com/comment/{post_ph}"
                print("Number of windows:", len(driver.window_handles))

                original_window = driver.current_window_handle

                driver.execute_script(f"window.open('{commentLink}');")
                time.sleep(1)
                # reload

                new_window = [
                    window for window in driver.window_handles if window != original_window][0]
                driver.switch_to.window(new_window)
                toFindinLike = "लाइक"

                maxTriesFind = 5
                tries = 0
                while toFindinLike not in driver.page_source:
                    driver.refresh()
                    time.sleep(2)
                    tries += 1

                    if tries > maxTriesFind:
                        break

                if tries > maxTriesFind:
                    driver.close()
                    driver.switch_to.window(original_window)
                    continue
                
                time.sleep(1)

                topBar = driver.find_element(
                    By.XPATH, '//ul[@class="List(n)  D(f) Ai(c) W(100%) H(100%) "]')
                # click on 3rd li

                idx = 0

                topEls = topBar.find_elements(By.XPATH, './li')
                for idx, li in enumerate(topEls):
                    if toFindinLike in li.text:
                        break

                likeCount = int(topEls[idx].text.replace(toFindinLike, '').strip())
                print("Likes: ", likeCount)
                # click
                topEls[idx].click()

                mainDiv = driver.find_element(
                    By.XPATH, '//div[@class="Ovy(a) Fxg(1) W(100%) Maw(600px) M(a)"]')

                # loadedlikes = number of a
                loaded_likes = len(mainDiv.find_elements(
                    By.XPATH, './/a[@data-cy="avatar-tag"]'))
                pbar = tqdm(total=likeCount)
                scroll_increment = 100  # The amount by which to increment the scroll each time
                current_scroll_position = 0  # Keep track of the current scroll position

                checkFinishTimer = 5
                startTimer = time.time()
                sameSize = False
                retried = False
                while not sameSize or not retried:
                    time.sleep(0.1)
                    driver.execute_script(
                        f"arguments[0].scrollTop = {current_scroll_position}", mainDiv)

                    if sameSize:
                        # scroll up a bit
                        retried = True
                        sameSize = False
                        driver.execute_script(
                            f"arguments[0].scrollTop = {current_scroll_position - 50}", mainDiv)

                        continue
                    current_scroll_position += scroll_increment

                    if time.time() - startTimer > checkFinishTimer:
                        listEls = mainDiv.find_elements(
                            By.XPATH, './/a[@data-cy="avatar-tag"]')
                        if len(listEls) == loaded_likes:
                            sameSize = True
                            if retried:
                                break

                        else:
                            retried = False
                            sameSize = False
                        loaded_likes = len(listEls)

                        pbar.update(loaded_likes - pbar.n)
                        startTimer = time.time()

                pbar.close()
                time.sleep(3)

                # get the list of all the users
                listEls = mainDiv.find_elements(
                    By.XPATH, './/a[@data-cy="avatar-tag"]')

                # in this, strong tag with data-cy="author-name" is the name of the user, get it
                # and add it to a list
                users = []
                for li in listEls:
                    # get href value
                    href = li.get_attribute('href')
                    # start after /profile/ from beginning and ?referrer=url from end
                    profile = href[href.find('/profile/') +
                                len('/profile/'):href.find('?referer=')]
                    users.append(profile)

                if authorID not in users:
                    users.append(authorID)

                print("Users:", users)
                print("Number of users:", len(users))
                driver.close()
                driver.switch_to.window(original_window)

                followers = {}

                for user in tqdm(users, desc="Getting followers"):
                    followers[user] = []
                    followerUrl = f"https://sharechat.com/profile/{user}/followers"
                    driver.execute_script(f"window.open('{followerUrl}');")
                    time.sleep(1)
                    # reload

                    new_window = [
                        window for window in driver.window_handles if window != original_window][0]
                    driver.switch_to.window(new_window)
                    time.sleep(1)

                    noContentText = "कोई यूज़र नहीं मिला"
                    # skip if no content
                    if noContentText in driver.page_source:
                        driver.close()
                        driver.switch_to.window(original_window)
                        continue

                    # to find all b with class="Fw(600)", keep scrolling page till no more b with class="Fw(600)" are found
                    # and add them to a list
                    current_scroll_position = 0
                    scroll_increment = 200

                    sameSize = False
                    retried = False

                    followSet = set()
                    loadedFollowers = 0

                    while not sameSize or not retried:
                        # scroll the main page
                        driver.execute_script(
                            "window.scrollTo(0, document.body.scrollHeight);")

                        time.sleep(1)

                        if sameSize:
                            # scroll up a bit
                            retried = True
                            sameSize = False
                            driver.execute_script(
                                "window.scrollTo(0, document.body.scrollHeight - 50);")
                            time.sleep(1)
                            continue

                        listEls = driver.find_elements(
                            By.XPATH, './/a[@data-cy="avatar-tag"]')

                        for els in listEls:
                            # //p[@class="Mb(2px) Whs(nw) Ovx(h) Tov(e) Maw(100%)"] text
                            elText = els.find_element(
                                By.XPATH, './/p[@class="Mb(2px) Whs(nw) Ovx(h) Tov(e) Maw(100%)"]').text
                            if elText not in followSet:
                                followSet.add(elText)
                        if len(followSet) == loadedFollowers:
                            sameSize = True
                            if retried:
                                break

                        else:
                            retried = False
                            sameSize = False
                        loadedFollowers = len(followSet)

                    # get text from b tags removing the initial @
                    for li in followSet:
                        followers[user].append(li)

                    # print("Followers:", followers[user])
                    # print("Number of followers:", len(followers[user]))
                    driver.close()
                    driver.switch_to.window(original_window)
                curData = {
                    "post_ph": post_ph,
                    "author_name": author_name,
                    "author_url": author_link,
                    "author_id": authorID,
                    "number_of_views": number_of_views,
                    "years_before": years_before,
                    "post_caption": pcText,
                    "likes": likeCount,
                    "users": users,
                    "followers": followers,
                    "tag": tag_url
                }
                print("Data:", curData)

                outputJsonL.write(json.dumps(curData) + '\n')
                outputJsonL.flush()
                postsDone += 1

            except KeyboardInterrupt:
                keepRunning = False
                print("Keyboard Interrupt... Exiting")
                break
            except Exception as e:
                print("An error occurred:", str(e))
                continue

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(5)
        if not newPosts or postsDone >= perTagLimit:
            break

        if not keepRunning:
            break

outputJsonL.close()


# In[ ]:


driver.quit()

