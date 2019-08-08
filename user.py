import sys
from spider import *


class User:
    def __init__(self, uid=0):      # default or uid=0 to generate an invalid User as placeholder
        # intrinsic attributes
        self.usr_id = uid             # user id
        self.nickname = 0            # user's nickname
        self.gender = 0             # user's gender
        self.location = 0             # user's region
        self.fan_num = 0               # the number of fans
        self.tweet_num = 0              # the number of tweets
        self.last_tweet_time = null_time        # when the user last tweeted a original content
        if uid != 0:
            self.get_info()
        # tree node attributes
        self.dist = 0              # distance to root during BFS
        self.follow_uid_list = self.get_follow_list()  # valid follow list
        self.in_degree = 0            # a degree indicates how much the user is followed
        self.bidirectional_follow = 0       # following each other is considered as a strong connection

    def show(self, file=sys.stdout):
        if self.usr_id != 0:
            print("Nickname:    %s" % self.nickname, file=file)
            print("Gender:      %s" % self.gender, file=file)
            print("Region:      %s" % self.location, file=file)
            print("Followers:   %d" % self.fan_num, file=file)
            print("Tweets:      %d" % self.tweet_num, file=file)
            print("Last Tweet:  ", end='', file=file)
            if self.last_tweet_time != null_time:
                print(self.last_tweet_time, file=file)
            else:
                print("Null", file=file)
            print("Home Page:   https://weibo.com/%d" % self.usr_id, file=file)
        else:
            print("NoneUser", file=file)

    def get_info(self):           # get valid intrinsic attributes
        self.nickname, self.gender, self.location \
            = self.get_items_from_info_page()
        self.fan_num, self.tweet_num, self.last_tweet_time \
            = self.get_items_from_profile()

    def get_follow_list(self):
        if self.usr_id == 0:
            return []

        follow_uids = []
        total_page_num = self.get_follow_page_num()
        for pg in range(1, total_page_num+1):
            follow_uids += self.get_follow_in_page(pg)
        return follow_uids

    def get_items_from_info_page(self):
        return except_wrapper_func(get_items_from_info_page, self.usr_id)

    def get_items_from_profile(self):
        return except_wrapper_func(get_items_from_profile, self.usr_id)

    def get_follow_page_num(self):
        return except_wrapper_func(get_follow_page_num, self.usr_id)

    def get_follow_in_page(self, pg):
        return except_wrapper_func(get_follow_in_page, self.usr_id, pg)


if __name__ == "__main__":
    user_id = 0              # put user ID here
    user = User(user_id)
    user.show()                  # check if User works well
    print(user.follow_uid_list)
