import requests
from datetime import datetime
import pandas as pd
import random
from random import choice
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv('REDDIT_API_CLIENT')
client_secret = os.getenv('REDDIT_API_SECRET')

warning_message = """This is a reminder to please read and follow:

* [Our rules](https://www.reddit.com/r/ask/about/rules)
* [Reddiquette](https://www.reddithelp.com/hc/en-us/articles/205926439)
* [Reddit Content Policy](https://www.redditinc.com/policies/content-policy)

When posting and commenting.

---

Especially remember Rule 1: `Be polite and civil`.

* Be polite and courteous to each other. Do not be mean, insulting or disrespectful to any other user on this subreddit.
* Do not harass or annoy others in any way.
* Do not catfish. Catfishing is the luring of somebody into an online friendship through a fake online persona. This includes any lying or deceit.

---

You *will* be banned if you are homophobic, transphobic, racist, sexist or bigoted in any way.

---


*I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](/message/compose/?to=/r/ask) if you have any questions or concerns.*"""

# For comment reddits
def get_top_comments(subreddit, post_id, n_comments=10, client_id="ZSyRcpI04o1wMb6Krzal2Q", client_secret="hK2dxtF-jPPwcWd3TvaUozSQoT2cug"):
    """Gets comments from the post chosed by the get_posts function

subreddit:
    name of the subreddit to scrape a post from
post_id:
    id of post returned from get_posts function
n_comments:
    # of comments to scrape
client_id:
    client key for access to reddit API
client_secret:
    client secret for access to reddit API

Returns: string of correctly formatted comments
"""
    comments_list = []

    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    headers = {
        "User-Agent": "AutoSnapComment 0.0.1"
    }
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "over18": "true"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        comments = data[1]["data"]["children"]
        for i, comment in enumerate(comments[:n_comments]):
            if "https://" not in comment['data']['body']:
                comments_list.append(f"$newcomment${i+1}. u/{comment['data']['author']}: $commentstart${comment['data']['body']}")

        print(f"\nTop {n_comments} comments retrieved successfully.\n")

    else:
        print(
            f"\nFailed to retrieve top comments. Response code: {response.status_code}\n")

    return "".join(comments_list)

def get_posts(subreddit, n_posts=100, filter='top', client_id="ZSyRcpI04o1wMb6Krzal2Q", client_secret="hK2dxtF-jPPwcWd3TvaUozSQoT2cug"):
    """Gets post chosen at random from desired category

subreddit:
    name of the subreddit to scrape a post from
n_posts:
    # of posts to scrape through
filter:
    category of the type of post ('top', 'new', 'trending')
client_id:
    client key for access to reddit API
client_secret:
    client secret for access to reddit API

Returns: info_dict of reddit information
"""
    info_dict = {}

    url = f"https://www.reddit.com/r/{subreddit}/{filter}/.json?limit={n_posts}"
    headers = {
        "User-Agent": "AutoSnapPost 0.0.1"
    }
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "over18": "true"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        print("\nNew post found successfully!\n")
        data = response.json()
        posts = data["data"]["children"]
        post = random.choice(posts)
        post_data = post["data"]
        info_dict["Subreddit"] = post_data['subreddit']
        info_dict["TextType"] = "Comment"
        info_dict["Title"] = post_data['title']
        info_dict["Author"] = post_data['author']
        info_dict["Url"] = post_data['url']
        info_dict["Id"] = post_data['id']
        textbody = get_top_comments(subreddit, post_data['id'])
        info_dict["TextBody"] = textbody.replace(warning_message, '')
        info_dict["DateScraped"] = str(datetime.now())[:19]
        info_dict["PostRank"] = str(posts.index(post)) + f"/{n_posts}"

    else:
        print(
            f"Failed to retrieve top posts. Response code: {response.status_code}")

    return info_dict

# For story reddits
def get_story(subreddit, n_posts=100, filter='top', client_id="ZSyRcpI04o1wMb6Krzal2Q", client_secret="hK2dxtF-jPPwcWd3TvaUozSQoT2cug"):
    """Gets comments from the post chosed by the get_posts function

subreddit:
    name of the subreddit to scrape a post from
n_posts:
    # of posts to scrape through
filter:
    category of the type of post ('top', 'new', 'trending')
client_id:
    client key for access to reddit API
client_secret:
    client secret for access to reddit API

Returns: info_dict of reddit information
"""

    info_dic = {}

    url = f"https://www.reddit.com/r/{subreddit}/{filter}/.json?limit={n_posts}"
    headers = {
        "User-Agent": "AutoReddit 0.0.1"
    }
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "over18": "true"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        posts = data["data"]["children"]
        post = random.choice(posts)
        post_data = post["data"]
        info_dic["Subreddit"] = post_data['subreddit']
        info_dic["TextType"] = "Story"
        info_dic["Title"] = post_data['title']
        info_dic["Author"] = post_data['author']
        info_dic["Url"] = post_data['url']
        info_dic["Id"] = post_data['id']
        textbody = post_data['selftext']
        info_dic["TextBody"] = textbody.replace(warning_message, '')
        info_dic["DateScraped"] = str(datetime.now())[:19]
        info_dic["PostRank"] = str(posts.index(post)) + f"/{n_posts}"
        print("Story retrieved successfully")

    else:
        print(
            f"Failed to retrieve top posts. Response code: {response.status_code}")

    return info_dic

# Final random scrape
def reddit_scraper(name):
    """Scrapes Reddit at random to find new content to create videos

Returns: info_dict of the recent scrape"""

    num = choice([1, 2])
    if num == 1:
        with open(f'Data/{name}CommentSubreddits.txt', 'r', encoding='utf-16') as f:
            fread = f.readlines()
            lst = [x.replace("\n", "").strip() for x in fread]
            info_dict = get_posts(random.choice(lst))
            return info_dict

    elif num == 2:
        with open(f'Data/{name}StorySubreddits.txt', 'r', encoding='utf-16') as f:
            fread = f.readlines()
            lst = [x.replace("\n", "").strip() for x in fread]
            info_dict = get_story(random.choice(lst))
            return info_dict

    else:
        print("\nScraper isnt working. Access keys to Reddit API are likely out of date.\n")
        return False
