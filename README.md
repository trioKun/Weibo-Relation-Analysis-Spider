# Weibo-Relation-Analysis-Spider
A multi-threading analysis spider in Python which helps you analyse the user-relative network in Weibo.

This project is based on dataabc/weiboSpider ( https://github.com/dataabc/weiboSpider ). Thanks to the contributors!

使用说明

1）下载脚本文件到某个文件夹下，安装所需的库或模块。确认能够访问weibo.cn，保持网络畅通。

2）weibo.cn通过检查cookie来判定登陆状态，因此在运行分析器(analyzer)之前，你首先必须拥有至少一个搜索无关的微博账号，即保证该账号不在你的搜索范围内，在此我们称之为爬虫账号。爬虫账号也可以在某宝上购买，参考价格为白号1元/个。

3）登录爬虫账号，进入weibo.cn页面，并获取此时的cookie值，将其填入settings.py文件指定位置。如果你有多个爬虫账号，请分别将相应cookie按相同格式填入，这将有助于加快运行速度。需要注意的是，使用同一浏览器登录获取的cookie值将在退出登录后失效，因此一个浏览器只能获取一个有效cookie。如果你有对于此问题的解决方案，欢迎与我沟通。

4）你还需要获取搜索根用户（搜索的起点）的uid。对于大多数用户，其uid通常为微博主页url末尾的10位数字。对于部分具有英文id的用户，其数字uid可在其weibo.cn主页下的“资料”页的url中获取。

5）填入至少一个cookie并获得uid后，先运行spider.py下的check_cookies与check_headers检查cookies与headers能否正常工作，如果all_headers中某项不能正常工作，请直接删去该项。对于任意一个uid，可以通过运行general_check检查爬虫能否正常工作。

6）完成前5条后，你已经完成了所有准备工作。现在，你只需要在analyzer.py中填入相应参数，指定根用户uid与搜索最大层次level，即可运行脚本开始爬取数据并分析。越高的层次所需的分析时间越长，2-3层的分析一般需要15-60分钟，具体取决于关系网的广度。

7）自定义部分：你可以按照实际情况选择最大子线程数threads，这一般取决于你所有的cookie数。一方面，提高子线程并发程度将有助于缓和request响应慢的问题，从而加快程序运行，另一方面，高并发带来的高request频率将提高网页无响应的概率，从而减慢程序运行。你也可以自定义analyzer.py中的scoring函数，该函数用于计算决定输出排序的关系得分(Relation Score)，该得分用于表征对应用户与根用户关系网的相关程度，你可以按自己的标准更改scoring中的各项权重，甚至可以增加其他的相关项。



程序说明


有效用户判定系统

1）本脚本的早期版本并未引入该系统，使得用户搜索范围过大，即便低层次的搜索也需要花费数小时，同时搜索结果包含大量垃圾用户，使得分析结果的价值大大降低。

2）本系统旨在分辨用户有效性，即该用户是否实际处于关系网内。由于部分用户没有很好地维护关注列表，因此基于关系链的搜索也可能引入“垃圾用户”，这些用户对于分析而言没有价值，徒增了分析的复杂度。

3）为了实现有效用户的判定，
