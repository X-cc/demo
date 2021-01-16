import networkx as nx
import random
import matplotlib.pyplot as plt
import community
import metis
import re
import numpy as np


def get_graph(file):
        G = nx.Graph()
        with open(file) as text:
            for line in text:
                vertices = line.strip().split(" ")
                source = int(vertices[0])
                target = int(vertices[1])
                G.add_edge(source,target)
            return G

def genflow(hosts):
    flow = {}
    nodes = list(hosts)
    for src in nodes:
        bw = random.gammavariate(1,1)
        dst = random.choice(nodes)
        while src == dst:
            dst = random.choice(nodes)
        flow[(src,dst)] = bw
    return flow

def getpathlink(path,swlink):
    links = []
    for i in range(1,len(path)-2):
        if (path[i], path[i + 1]) in swlink:
            link = [path[i], path[i + 1]]
        else:
            link = [path[i + 1], path[i]]
        links.append((link[0], link[1]))
    return links

class Graphbasic(object):
    def __init__(self,G):
        #self._G_cloned = Q.clone_graph(G)
        self._G = G
        self._partition = [[n for n in G.nodes()]]
        self._max_Q = 0.0
        self._paths = {}
        self._link = []


    def getpath(self,hosts):
        # paths = {}
        nodes = hosts
        # print(nodes)
        for node in nodes:
            for dst in nodes:
                if dst != node:
                    path = nx.all_shortest_paths(G, source=node, target=dst)
                    # print(list(path))
                    self._paths["(%s,%s)" % (node, dst)] = [p for p in path]
        return self._paths

    def getlink(self):
        self._link = list(self._G.edges)
        return self._link

def add_host(hosts):#hosts是一个字典
    for k,v in hosts.items():
        G.add_edge(k,v)


def calculateimportance(paths,swlink,importance,parts_host):
    num = 0 #计算跨区域最短路径数
    for k,v in paths.items():
        # print(k)
        s,d = re.findall(r"\d+",k)
        # print(s,d)
        if parts_host[int(s)-1]==parts_host[int(d)-1]:#两个host在同一个区域，跳过，只计算跨区域路径
            continue
        num += 1
        n = len(v)
        for path in v:
            links = getpathlink(path,swlink)
            for i in links:
                importance[i] += 1/n

    for k,v in importance.items():
        importance[k] = v / num
    return importance

def getprobepath(probe,paths,swlinks,probe_station):
    probe_paths = {}
    probe_links = []
    
    while len(probe)!=0:
        max = []
        probe_path = []
        probe_sd = None
        cost=0
        for k,v in paths.items():
            for i in v:
                path_links =  getpathlink(i,swlinks)
                # print(path_links)
                # print(probe)
                tmp =  [i for i in probe if i in path_links]
                # print(tmp)
                if len(tmp) == 0:
                    continue
                else:
                    tmp_cost = len(tmp) / len(path_links) + 2  # 计算代价，+2是两端点代价
                    # print(tmp)
                    if len(tmp)>len(max):
                    # if tmp_cost > cost:
                        cost = tmp_cost
                        # print(tmp)
                        max = tmp
                        probe_path = i
                        probe_sd = k

        print(probe_path)
        s, d = re.findall(r"\d+", str(probe_sd))
        # print(s, d)
        probe_station.add(s)
        probe_station.add(d)
        probe_paths[probe_sd] = probe_path
        probe_links += getpathlink(probe_path,swlinks)
        for i in max:
            probe.remove(i)
    return probe_paths,probe_links,probe_station

def host_split(full_list, ratio, shuffle=False):
    """
    数据集拆分: 将所有节点按比例ratio（随机）划分为2个子列表sublist_1与sublist_2
    :param full_list: 数据列表
    :param ratio:     比例
    :param shuffle:   是否随机划分
    :return:
    """
    n_total = len(full_list)
    offset = int(n_total * ratio)
    if n_total == 0 or offset < 1:
        return [], full_list
    if shuffle:
        random.shuffle(full_list)
    sublist_1 = full_list[:offset]
    return sublist_1

G_ba50 = get_graph('ba50.txt')
G_ba50_host_30 = {'h1': 23, 'h2': 45, 'h3': 41, 'h4': 21, 'h5': 22, 'h6': 48, 'h7': 44, 'h8': 11, 'h9': 43, 'h10': 36, 'h11': 8, 'h12': 5, 'h13': 2, 'h14': 34, 'h15': 20}
probe_station = {'10', '14', '5', '3', '6', '7', '1', '4', '15', '8', '2', '12', '9'}
if __name__=='__main__':
    G = G_ba50
    Gb = Graphbasic(G)
    ##待测路径比例
    r = 0.5
    ##有host的节点比例
    r_host = 0.5
    hosts = G_ba50_host_30

    # sw_with_host = host_split(list(G.nodes),r_host,True)
    # hosts = {}
    # for i, sw in enumerate(sw_with_host):
    #     hosts['h%s' % (i + 1)] = sw
    # print(hosts)
    ##给每条链路定带宽
    bw = {}
    for i in list(G.edges()):
        bw[i]=5
    print(bw)
    # part = community.best_partition(G)#community 分区方法
    # G =  nx.windmill_graph(4,5)
    [counts,parts]=metis.part_graph(G,10)# metis 分区方法

    print('节点：',G.nodes)
    print('分区：',parts)
    ##分区绘图
    pos = nx.spring_layout(G)
    colors = ['red', 'blue', 'green', 'yellow', 'pink','orange','purple','gray','brown','olive','cyan']
    color_value = []
    for i, p in enumerate(parts):
        color_value.append(colors[p])
    nx.draw_spring(G, cmap=plt.plot(), node_color=color_value, node_size=100, with_labels=True)
    plt.show()


    # 不包含hostlink的链路集，用于统计链路传输特性
    swlinks = Gb.getlink()


    # 每个host的分区
    parts_host = {}
    for host, sw in enumerate(hosts.values()):
        parts_host[host] = parts[int(sw) - 1]


    ##分区完成，加入host
    add_host(hosts)
    plt.plot()
    # nx.draw_spring(G, node_size=100, with_labels=True)
    # plt.show()


    ##计算端到端路径
    # print(Gb._G.nodes)
    paths = Gb.getpath(list(hosts.keys()))
    print('端到端路径：',paths)

    ##每条链路的故障概率
    faultrate = {}
    for i in swlinks:
        faultrate[i] = 0

    faultrate = {}
    importance = {}
    for i in swlinks:
        faultrate[i] = 0
        importance[i] = 0

    ##计算链路的传输重要性
    calculateimportance(paths, swlinks, importance, parts_host)
    print('importance:',importance)

    set_importance = set()
    for i in importance.values():
        set_importance.add(i)
    importance = dict(sorted(importance.items(), key=lambda item:item[1], reverse=True)) # importance按值排序
    print('sorted importance:',importance)

    ##按待测路径比例r选出待测链路
    probe = [k for k,v in importance.items()]
    probe = probe[0:int(len(probe)*r)]
    print('probe link',probe)

    probe_paths, probe_links,probe_station = getprobepath(probe[:], paths, swlinks)
    print('probe', probe)
    print('probe_paths', probe_paths)
    print('probe_links', probe_links)
    print('probe_station', probe_station)

    ##监测到的区域
    mpart = set()  # 监测到的part
    for k in probe_links:
        s, d = re.findall(r"\d+", str(k))
        # print(s, d)
        mpart.add(parts[int(s)])
        mpart.add(parts[int(d)])

    all_link_probe_paths,all_link_probe_links,all_link_probe_station = getprobepath([k for k,v in importance.items()],paths,swlinks)
    print('all_link', swlinks)
    print('all_link_probe_paths', all_link_probe_paths)
    print('all_link_probe_links', all_link_probe_links)
