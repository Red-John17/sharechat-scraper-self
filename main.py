#!/usr/bin/env python
# coding: utf-8

# In[3]:

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
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Flask, request
from flask_cors import CORS, cross_origin
import threading

nltk.download('vader_lexicon')

tag_urls = ["https://sharechat.com/tag/mB8Gl1", "https://sharechat.com/tag/BJd7kd", "https://sharechat.com/tag/r1A9QK", "https://sharechat.com/tag/Ab66zl", "https://sharechat.com/tag/nkOQN",
            "https://sharechat.com/tag/9pzqRa"]
perTagLimit = 20
outputName = 'output.jsonl'


def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)
# In[4]:


# Set the display environment variable
os.environ['DISPLAY'] = ':1'
# URL of the ShareChat page
def run():
    
    url = "https://sharechat.com/trending/Hindi"
    chromedriver_autoinstaller.install()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-popup-blocking')
    # Overcomes limited resource problems
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # Applicable to windows os only
    chrome_options.add_argument(
        "--remote-debugging-port=9222")  # This is important
    # Disable sandboxing that Chrome runs in.
    chrome_options.add_argument("--no-sandbox")

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
    st = time.time()
    for tag_url in tag_urls:
        if not keepRunning:
            break
        postsDone = 0
        driver.get(tag_url)
        while keepRunning:
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
                    toFindinComment = "कमेंट"

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

                    likeCount = int(topEls[idx].text.replace(
                        toFindinLike, '').strip())
                    print("Likes: ", likeCount)

                    idx2 = 0
                    for idx2, li in enumerate(topEls):
                        if toFindinComment in li.text:
                            break

                    commentCount = int(topEls[idx2].text.replace(
                        toFindinComment, '').strip())
                    print("Comments: ", commentCount)

                    # COMMENTS SCRAPING
                    mainDiv = driver.find_element(
                        By.XPATH, '//div[@class="Ovy(a) Fxg(1) W(100%) Maw(600px) M(a)"]')

                    loadedComments = len(mainDiv.find_elements(
                        By.XPATH, './/div[@class="Px($sm) Pt($xs) Mb($xs) Bgc($white)"]'))

                    pbar = tqdm(total=commentCount)
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
                                By.XPATH, './/div[@class="Px($sm) Pt($xs) Mb($xs) Bgc($white)"]')
                            if len(listEls) == loadedComments:
                                sameSize = True
                                if retried:
                                    break

                            else:
                                retried = False
                                sameSize = False
                            loadedComments = len(listEls)

                            pbar.update(loadedComments - pbar.n)
                            startTimer = time.time()

                    pbar.close()
                    time.sleep(3)

                    # get the list of all the comments
                    listEls = mainDiv.find_elements(
                        By.XPATH, './/div[@class="Px($sm) Pt($xs) Mb($xs) Bgc($white)"]')

                    comments = {}
                    users = []
                    for li in listEls:
                        nameA = li.find_elements(
                            By.XPATH, './/a[@class="Lh(20px) Mb($xs) Pend($xs) Whs(nw) Ovx(h) Tov(e) Maw(100%) C($bcBlue)"]')

                        if len(nameA) == 0:
                            continue

                        if len(nameA) > 1:
                            print("More than 1 nameA in comments")
                            continue

                        # get href
                        href = nameA[0].get_attribute('href')
                        # start after /profile/ from beginning, no need to find ?referrer=url from end
                        profile = href[href.find('/profile/') +
                                    len('/profile/'):]

                        users.append(profile)

                        if profile not in comments:
                            comments[profile] = []

                        contentDiv = li.find_elements(
                            By.XPATH, './/div[@class="Pend($2xl)"]')
                        if len(contentDiv) == 0:
                            continue

                        commentStructure = {"text": "",
                                            "images": [], "sentiment": "N/A"}
                        for div in contentDiv:
                            # get text from div
                            text = div.text
                            # add all img sources
                            imgs = div.find_elements(By.XPATH, './/img')
                            for img in imgs:
                                commentStructure["images"].append(
                                    img.get_attribute('src'))
                            commentStructure["text"] += text
                            if len(commentStructure["text"]) > 0:
                                commentStructure["sentiment"] = analyze_sentiment(
                                    commentStructure["text"])

                        comments[profile].append(commentStructure)

                    print("Comments:", comments)

                    # LIKES SCRAPING
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

                    justLikes = []
                    for li in listEls:
                        # get href value
                        href = li.get_attribute('href')
                        # start after /profile/ from beginning and ?referrer=url from end
                        profile = href[href.find('/profile/') +
                                    len('/profile/'):href.find('?referer=')]
                        users.append(profile)
                        justLikes.append(profile)

                    if authorID not in users:
                        users.append(authorID)

                    users = list(set(users))

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
                        "comments": comments,
                        "like_users": justLikes,
                        "all_users": users,
                        "followers": followers,
                        "tag": tag_url
                    }
                    print("Data:", curData)

                    outputJsonL.write(json.dumps(curData) + '\n')
                    outputJsonL.flush()
                    postsDone += 1

                    if postsDone >= perTagLimit:
                        break

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
    et = time.time()
    print("Time taken:", et - st)
    # save to file too
    with open('timeTaken.txt', 'w') as f:
        f.write(str(et - st))
        


    # In[ ]:


    driver.quit()

def background_scrape():
    """Function to run the scrape in the background."""
    run() 


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/scrape', methods=['POST'])
@cross_origin(supports_credentials=True, origins='*')
def scrape_data():
    global perTagLimit, outputName, tag_urls
    
    try:
        maxCount = request.json['maxCount']
        perTagLimit = maxCount
    except:
        pass
    try:
        outputNameL = request.json['outputName']
        outputName = outputNameL
    except:
        pass

    try:
        tag_urlsL = request.json['tag_urls']
        tag_urls = tag_urlsL
    except:
        pass
    
    thread = threading.Thread(target=background_scrape)
    thread.start()

    return f"Scraping started with maxCount: {perTagLimit}, outputName: {outputName}, tag_urls: {tag_urls}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)