from user import *
import threading


# you can modify scoring function below if you like
def scoring(user):              # weight in analyzer output order
    return user.in_degree + user.bidirectional_follow - 2 ** (user.fan_num / 300) + 30


# MultiThreading solving the too long answering time problem
class GetUser(threading.Thread):
    def __init__(self, uid, pa_ind, ch_ind):
        threading.Thread.__init__(self)
        self.uid = uid
        self.pa_index = pa_ind
        self.ch_index = ch_ind

    def run(self):
        new_usr = User(self.uid)
        Analyzer.usr_nodes_mutex.acquire()
        Analyzer.usr_nodes[self.ch_index] = new_usr
        Analyzer.usr_nodes[self.ch_index].dist = Analyzer.usr_nodes[self.pa_index].dist + 1
        Analyzer.usr_nodes_mutex.release()


class Analyzer:
    usr_nodes = []        # containing all detected users
    usr_nodes_mutex = threading.Lock()

    def __init__(self, uid, level=2, child_threads=3):
        """
        :param uid: the user id of the root user
        :param level: search level, 2 or 3 is recommended
        :param child_threads: max number of child threads, depends on the number of your cookies
        """
        self.root_uid = uid
        self.threads = 1 + child_threads        # maximum child child_threads
        self.bfs(level)           # construct relationship graph by BFS

    def bfs(self, level):           # search until [level]st level
        cert = list()           # certifications, decides whether to put a user into usr_nodes
        # value of cert[i]:
        Certed = 2**level         # get certificated
        Init_Cert = 0
        Pot_Cert = range(0, Certed)      # Potential certificated. but not enough followed, looking for another
        Not_Cert = -1               # No certificated. be blocked due to certain filter strategy
        Exist = Certed + 1         # already existed usr_nodes

        uids = list()        # uid[i] <==> cert[i]
        uids.append(self.root_uid)
        self.usr_nodes.append(User(self.root_uid))
        cert.append(Exist)
        self.usr_nodes[0].dist = 0
        self.usr_nodes[0].in_degree = 0
        curr = 0
        last_level = -1

        while True:
            self.usr_nodes_mutex.acquire()
            curr_user = self.usr_nodes[curr]
            self.usr_nodes_mutex.release()

            if curr_user.dist != last_level:
                print("current level is %d" % curr_user.dist)
                last_level = curr_user.dist
            print("\t %d.scanning uid %d..." % (curr, curr_user.usr_id))

            for follow_uid in curr_user.follow_uid_list:
                if follow_uid not in uids and curr_user.dist < level:     # follow_uid is not yet collected
                    uids.append(follow_uid)
                    cert.append(Init_Cert)

                if follow_uid in uids:
                    u_ind = uids.index(follow_uid)
                    if curr_user.dist < level and cert[u_ind] in Pot_Cert:
                        cert[u_ind] += 2**(level - curr_user.dist)
                        if cert[u_ind] == Certed:
                            MaxNoTweetDays = 180      # filter, ignore users who didn't tweet for a number of days
                            if calc_days_until_now(self.get_last_tweet_time(follow_uid)) > MaxNoTweetDays:
                                cert[u_ind] = Not_Cert
                            else:
                                cert[u_ind] = Exist
                                print("\t\t found new uid %d" % follow_uid)

                                self.usr_nodes_mutex.acquire()
                                ins_index = len(self.usr_nodes)
                                self.usr_nodes.append(User())              # a empty User object as a placeholder
                                self.usr_nodes_mutex.release()

                                while threading.activeCount() >= self.threads:
                                    time.sleep(0.1)
                                GetUser(follow_uid, curr, ins_index).start()
                    elif cert[u_ind] == Exist:           # increase corresponding attributes
                        self.usr_nodes_mutex.acquire()
                        n_ind = self.index_usr_node(follow_uid)
                        self.usr_nodes_mutex.release()
                        while n_ind == -1:
                            time.sleep(0.1)            # wait until thread works it out
                            self.usr_nodes_mutex.acquire()
                            n_ind = self.index_usr_node(follow_uid)
                            self.usr_nodes_mutex.release()

                        self.usr_nodes_mutex.acquire()
                        # divide (dist+1) because dist could be 0
                        self.usr_nodes[n_ind].in_degree += 1 / (curr_user.dist + 1)
                        if curr_user.usr_id in self.usr_nodes[n_ind].follow_uid_list:  # follow each other
                            self.usr_nodes[curr].bidirectional_follow += 1 / (self.usr_nodes[n_ind].dist + 1)
                            self.usr_nodes[n_ind].bidirectional_follow += 1 / (curr_user.dist + 1)
                        self.usr_nodes_mutex.release()
            curr += 1

            self.usr_nodes_mutex.acquire()
            over = bool(curr >= len(self.usr_nodes))
            self.usr_nodes_mutex.release()
            if over:
                break

            while True:
                self.usr_nodes_mutex.acquire()
                work_out = bool(self.usr_nodes[curr].usr_id != 0)
                self.usr_nodes_mutex.release()
                if work_out:
                    break
                time.sleep(0.1)              # wait until thread works it out


    @staticmethod
    def get_last_tweet_time(uid):
        return except_wrapper_func(get_last_tweet_time_fullver, uid)

    def output(self, file=sys.stdout):
        for user in sorted(self.usr_nodes, key=scoring, reverse=True):
            if user.dist >= 1 and user.usr_id != 0:
                user.show(file=file)
                print("Relation Level:    %d" % user.dist, file=file)
                print("Relation Score:    %d" % round(scoring(user)), file=file)
                print(file=file)

    def index_usr_node(self, uid):
        """
        :param uid: an int, the target uid
        :return: the index of User of the specific uid
        """
        index = 0
        while index < len(self.usr_nodes) and self.usr_nodes[index].usr_id != uid:
            index += 1
        if index < len(self.usr_nodes):
            return index
        else:
            return -1


if __name__ == "__main__":
    print(Datetime.now())
    user_id = 0              # put user ID here
    result = Analyzer(user_id)
    print(Datetime.now())
    
    import os
    curr_path = os.path.dirname(__file__)
    res_file = open(curr_path + r"\analysis_result.txt", "w")
    result.output(file=res_file)
    res_file.close()
