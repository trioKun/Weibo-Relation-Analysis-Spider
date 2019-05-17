from user import *
import threading


# You can modify scoring function below if you like
def scoring(user):              # weight in analyzer output order
    return user.in_degree + user.bidirectional_follow - 2 ** (user.fan_num / 300) + 30


# MultiThreading solving the too long answering time problem
class Thread(threading.Thread):
    def __init__(self, uid, pa_ind, ch_ind):
        threading.Thread.__init__(self)
        self.uid = uid
        self.pa_index = pa_ind
        self.ch_index = ch_ind

    def run(self):
        Analyzer.usr_nodes[self.ch_index] = User(self.uid)
        Analyzer.usr_nodes[self.ch_index].dist = Analyzer.usr_nodes[self.pa_index].dist + 1


class Analyzer:
    usr_nodes = []        # containing all detected users

    def __init__(self, uid, level=2, threads=5):
        """
        :param uid: the user id of the root user
        :param level: search level, 2 or 3 is recommended
        :param threads: max number of child threads, depends on the number of your cookies
        """
        self.root_uid = uid
        self.threads = 1 + threads        # maximum threads
        self.bfs(level)           # construct relationship graph by BFS

    # Using a valid user identification system. I will explain it in README.md file.
    def bfs(self, level):           # search until [level]st level
        cert = list()           # certifications, decides whether to put a user into usr_nodes
        # value of cert[i]:
        Certed = 2 ** level         # get certificated
        Pot_Cert = range(1, Certed)      # Potential certificated. but not enough followed, looking for another
        Not_Cert = 0               # No certificated. be blocked due to certain filter strategy
        Exist = Certed + 1         # already existed usr_nodes

        uids = list()        # uid[i] <==> cert[i]
        uids.append(self.root_uid)
        self.usr_nodes.append(User(self.root_uid))
        cert.append(Exist)
        self.usr_nodes[0].dist = 0
        self.usr_nodes[0].in_degree = 0
        curr = 0
        last_level = -1
        while curr < len(self.usr_nodes) and self.usr_nodes[curr].dist <= level:
            for follow_uid in self.usr_nodes[curr].follow_uid_list:
                if follow_uid in uids:
                    u_ind = uids.index(follow_uid)
                    if cert[u_ind] in Pot_Cert:
                        cert[u_ind] += 2 ** (level - self.usr_nodes[curr].dist)
                        if cert[u_ind] == Certed:
                            if calc_days_until_now(self.get_last_tweet_time_fullver(follow_uid)) > 365:
                                # filter, ignore users who didn't tweet for a number of days
                                cert[u_ind] = Not_Cert
                            else:
                                cert[u_ind] = Exist
                                ins_index = len(self.usr_nodes)
                                self.usr_nodes.append(User())
                                while threading.activeCount() >= self.threads:
                                    time.sleep(0.1)
                                Thread(follow_uid, curr, ins_index).start()
                    elif cert[u_ind] == Exist:           # increase corresponding attributes
                        n_ind = find_in_usrs(self.usr_nodes, follow_uid)
                        while n_ind == UserNotFound:
                            time.sleep(0.1)            # wait until thread works it out
                            n_ind = find_in_usrs(self.usr_nodes, follow_uid)
                        self.usr_nodes[n_ind].in_degree += 1 / (self.usr_nodes[curr].dist + 1)
                        if self.usr_nodes[curr].usr_id in self.usr_nodes[n_ind].follow_uid_list:  # follow each other
                            self.usr_nodes[curr].bidirectional_follow += 1 / (self.usr_nodes[n_ind].dist + 1)
                            self.usr_nodes[n_ind].bidirectional_follow += 1 / (self.usr_nodes[curr].dist + 1)
                elif self.usr_nodes[curr].dist < level:
                    uids.append(follow_uid)
                    if self.usr_nodes[curr].dist == 0:      # root's follow will be added unconditionally
                        cert.append(Exist)
                        ins_index = len(self.usr_nodes)
                        self.usr_nodes.append(User())
                        while threading.activeCount() >= self.threads:
                            time.sleep(0.1)
                        Thread(follow_uid, curr, ins_index).start()
                    else:
                        cert.append(2 ** (level - self.usr_nodes[curr].dist))
            curr += 1
            while curr < len(self.usr_nodes) and self.usr_nodes[curr].usr_id == 0:
                time.sleep(0.1)

    @staticmethod
    def get_last_tweet_time_fullver(uid):
        return except_wrapper_func(get_last_tweet_time_fullver, uid)

    def output(self, file=sys.stdout):
        for user in sorted(self.usr_nodes, key=scoring, reverse=True):
            if user.dist >= 1 and user.usr_id != 0:
                user.show(file=file)
                print("Relation Level:    %d" % user.dist, file=file)
                print("Relation Score:    %d" % round(scoring(user)), file=file)
                print(file=file)


if __name__ == "__main__":
    import os
    curr_path = os.path.dirname(__file__)
    res_file = open(curr_path + r"\analysis_result.txt", "w")
    user_id = 0        # put your uid here
    ana = Analyzer(user_id)
    ana.output(file=res_file)
    res_file.close()
