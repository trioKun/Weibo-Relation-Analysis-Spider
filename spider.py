import time
import random
import requests
from requests.exceptions import ReadTimeout,HTTPError,RequestException
from lxml import etree
from settings import *
from tools import *


def get_selector(url):
    """
    :param url:     a string, the url of certain page, begins with 'http://' or 'https://'
    :return:        the selector of the specified page
    """
    header = random.choice(all_headers)
    cookie = random.choice(all_cookies)
    html = requests.get(url, timeout=10, cookies=cookie, headers=header).content
    selector = etree.HTML(html)
    return selector


def get_nickname(sel):
    """
    :param sel:   the selector of info page
    :return:      a string, the user's nickname
    """
    info = sel.xpath("//title/text()")[0]
    nickname = info[:-3]                # for example,"NASA爱好者的资料"
    return nickname


def get_gender(sel):
    """
    :param sel:   the selector of info page
    :return:      a string, the user's gender
    """
    info = sel.xpath("//div[@class='c']/text()")
    gender = "unknown"
    for item in info:
        if item[:2] == "性别":            # for example, "性别:男"
            gender = item[3]
            break
    return gender


def get_location(sel):
    """
    :param sel:   the selector of info page
    :return:      a string, the user's region
    """
    info = sel.xpath("//div[@class='c']/text()")
    location = "unknown"
    for item in info:
        if item[:2] == "地区":            # for example, "地区:福建 厦门"
            location = item[3:]
            break
    return location


def get_items_from_info_page(uid):
    url = "https://weibo.cn/%d/info" % uid
    # It takes a long time to get a page, so we request as less as possible
    selector = get_selector(url)
    nickname = get_nickname(selector)
    gender = get_gender(selector)
    location = get_location(selector)
    return nickname, gender, location


def get_fan_num(sel):
    """
    :param sel: the selector of home page
    :return: an int, the number of fans
    """
    info = sel.xpath("//div[@class='u']/div[@class='tip2']/a/text()")[1]
    fans_num = int(info[3:-1])           # for example, "粉丝[489]"
    return fans_num


def get_tweet_num(sel):
    """
    :param sel: the selector of home page
    :return: an int, the number of tweets
    """
    info = sel.xpath(
        "//div[@class='tip2']/span[@class='tc']/text()")[0]
    tweet_num = int(info[3:-1])            # for example, "微博[1047]"
    return tweet_num


def get_last_tweet_time(sel):
    """
    :param sel: the selector of home page
    :return: Datetime, indicates when the user last tweet
    """
    info = sel.xpath("//div[@class='c']/div")
    if len(info) == 0 and len(sel.xpath("//div[@class='u']")) != 0:   # no public tweets
        return null_time

    last_tweet_index = 0     # find the real last tweet
    # ignore the stick-to-top tweet
    sticky = info[0].xpath("//div/span[@class='kt']/text()")
    if "置顶" in sticky:
        last_tweet_index += 1

    info = info[0].xpath("//span[@class='ct']/text()")
    # ignore meaningless tweets， may be several
    while "生日动态" in info[last_tweet_index] or "粉丝红包" in info[last_tweet_index]:
        last_tweet_index += 1

    info = info[last_tweet_index]
    str_time = info.split(u'\xa0')[0]
    tweet_time = format_time(str_time)
    return tweet_time


def get_items_from_profile(uid):
    url = r"https://weibo.cn/u/%d?filter=1" % uid      # filter=1 to get only original tweet
    selector = get_selector(url)
    fan_num = get_fan_num(selector)
    tweet_num = get_tweet_num(selector)
    last_tweet_time = get_last_tweet_time(selector)
    return fan_num, tweet_num, last_tweet_time


# Full version of get_last_tweet_time
def get_last_tweet_time_fullver(uid):
    url = r"https://weibo.cn/u/%d?filter=0" % uid
    selector = get_selector(url)
    return get_last_tweet_time(selector)


def get_follow_page_num(uid):
    """
    :param uid: an int, user id
    :return: an int, how many page there are in user's follows
    """
    url = r"https://weibo.cn/%d/follow" % uid
    selector = get_selector(url)
    info = selector.xpath("//div[@class='pa']/form/div/input/@value")
    if len(info) > 0:
        page_num = int(info[0])
    else:
        page_num = 1
    return page_num


def get_follow_in_page(uid, page_no):
    """
    :param uid: a int, user id
    :param page_no: a int, the page number
    :return: a list of int, containing all user ids of user's valid follows
    """
    url = "https://weibo.cn/%d/follow?page=%d" % (uid, page_no)
    selector = get_selector(url)
    info = selector.xpath("//table")
    if len(info) == 0 and len(selector.xpath("//div[@class='u']")) != 0:      # if there is not follow in this page
        return []
    else:
        info = info[0]

    follow_fans = [int(item[2:-1]) for item in info.xpath("//text()")
                   if item[:2] == "粉丝" and item[-1] == "人"]           # for example, "粉丝221人"
    follow_urls = info.xpath("//td[@valign][@style]/a[@href]/@href")
    # follow_urls[i] <==> follow_fans[i]
    follow_uids = []
    for i in range(len(follow_urls)):
        if follow_fans[i] < 1000:
            if follow_urls[i][:19] == "https://weibo.cn/u/":
                f_uid = int(follow_urls[i][19:])
            else:
                english_id = follow_urls[i][17:]
                f_uid = int(eid_to_uid(english_id))
            follow_uids.append(f_uid)
    return follow_uids


def eid_to_uid(eid):
    """
    :param eid: a string, the English id of a user
    :return: an int, the uid of the same user
    """
    url = r"https://weibo.cn/%s" % eid
    selector = get_selector(url)
    info = selector.xpath("//div[@class='u']")[0]\
        .xpath("//td[@valign='top']")[0]\
        .xpath("//div[@class='ut']")[0]\
        .xpath("//a[@href]/@href")
    uid = 0
    for item in info:
        if item[0] == "/" and item[-5:] == "/info":         # for example "/2206258462/info"
            uid = int(item[1:-5])
            break
    return uid


WebExcepts = (IndexError, AttributeError, ValueError,
             ReadTimeout, HTTPError, RequestException)


# exception wrapper function to solve no-answer and wrong-answer problem
def except_wrapper_func(func, *args):
    try:
        return func(*args)
    except WebExcepts:
        # Exceptions rise because of the page error in most cases
        if func == get_last_tweet_time_fullver:       # called by Analyzer.bfs directly
            max_wait_time = 30
        else:                         # called when a child thread during constructing User
            max_wait_time = 100
        # Once program don't get answer from website, sleep for a few seconds
        time.sleep(random.randrange(max_wait_time))
        return except_wrapper_func(func, *args)


# This function helps you check if spider.py works well with the specific uid
def general_check(uid):
    for item in get_items_from_info_page(uid):
        print(item)
    for item in get_items_from_profile(uid):
        print(item)
    page = get_follow_page_num(uid)
    for pg in range(1, page + 1):
        print("Page %d: " % pg, end='')
        print(get_follow_in_page(uid, pg))


# This function helps you check if all user agents works well
def check_headers(uid):
    url = r"https://weibo.cn/u/%d?filter=1" % uid
    cookie = random.choice(all_cookies)
    for header in all_headers:
        print(header)
        html = requests.get(url, timeout=10, cookies=cookie, headers=header).content
        selector = etree.HTML(html)
        try:
            print("work well:", get_last_tweet_time(selector))
        except Exception as e:
            print(e)
        print()
        time.sleep(0.3)


# This function helps you check if all cookies works well
def check_cookies(uid):
    url = r"https://weibo.cn/u/%d?filter=1" % uid
    header = random.choice(all_headers)
    for cookie in all_cookies:
        print(cookie)
        html = requests.get(url, timeout=10, cookies=cookie, headers=header).content
        selector = etree.HTML(html)
        try:
            print("work well:", get_last_tweet_time(selector))
        except Exception as e:
            print(e)
        print()
        time.sleep(0.3)


if __name__ == "__main__":
    user_id = 0
    general_check(user_id)
