import datetime


class Datetime(datetime.datetime):
    def __str__(self):
        return self.strftime('%Y-%m-%d %H:%M')


null_time = Datetime(1, 1, 1, 0, 0)


def format_time(str_time):
    """
    :param str_time: a string crawled from weibo.cn indicates the publish time
    :return: a Datetime expressing the actual time
    """
    if u"刚刚" in str_time:
        tweet_time = Datetime.now().strftime('%Y-%m-%d %H:%M')
    elif u"分钟" in str_time:
        minute = str_time[:str_time.find(u"分钟")]
        minute = datetime.timedelta(minutes=int(minute))
        tweet_time = (Datetime.now() - minute).strftime("%Y-%m-%d %H:%M")
    elif u"今天" in str_time:
        today = Datetime.now().strftime("%Y-%m-%d")
        clock = str_time[3:]
        tweet_time = today + " " + clock
    elif u"月" in str_time:
        year = Datetime.now().strftime("%Y")
        month = str_time[0:2]
        day = str_time[3:5]
        clock = str_time[7:12]
        tweet_time = (year + "-" + month + "-" + day + " " + clock)
    else:
        tweet_time = str_time[:16]
    # above lines turns str_time into a format of yyyy-mm-dd hh:mm

    tweet_time = Datetime(int(tweet_time[0:4]),      # year
                          int(tweet_time[5:7]),      # month
                          int(tweet_time[8:10]),     # day
                          int(tweet_time[11:13]),    # hour
                          int(tweet_time[14:16]))    # minute
    return tweet_time


def calc_days_until_now(time):
    """
    :param time: a Datetime object
    :return: how many days from time to present
    """
    duration = Datetime.now() - time
    return duration.days


UserNotFound = -1


def find_in_usrs(users, uid):
    """
    :param users: a list of User objects
    :param uid: an int, the target uid
    :return: the index of User of the specific uid or NotFound
    """
    ind = 0
    while ind < len(users) and users[ind].usr_id != uid:
        ind += 1
    if ind < len(users) and users[ind].usr_id == uid:
        return ind
    else:
        return UserNotFound


if __name__ == "__main__":
    print(null_time)
    print(calc_days_until_now(Datetime(1970, 1, 1)))
