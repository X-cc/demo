import networkx as nx
import random
import matplotlib.pyplot as plt
import community
import metis
import re
import random

def get_graph(file):
    G = nx.Graph()
    with open(file) as text:
        for line in text:
            vertices = line.strip().split(" ")
            if len(vertices) == 1:
                for i in range(1,int(vertices[0])+1):
                    G.add_node(str(i))
                continue
            source = vertices[0]
            if "e" in source:
                break
            target = vertices[1]
            G.add_edge(source, target)
        return G


def genflow(hosts):
    flow = {}
    nodes = list(hosts)
    for src in nodes:
        bw = random.paretovariate(2.5)
        dst = random.choice(nodes)
        while src == dst:
            dst = random.choice(nodes)
        flow[(src,dst)] = bw
    return flow


def getpathlink(path, swlink):
    links = []
    for i in range(1,len(path) - 2):
        if (path[i], path[i + 1]) in swlink:
            link = [path[i], path[i + 1]]
        else:
            link = [path[i + 1], path[i]]
        links.append((link[0], link[1]))
    return links


class Graphbasic(object):
    def __init__(self, G):
        # self._G_cloned = Q.clone_graph(G)
        self._G = G
        self._partition = [[n for n in G.nodes()]]
        self._max_Q = 0.0
        self._paths = {}
        self._link = []
        self._host = []

    def getpath(self):#host之间的最短路
        # paths = {}
        nodes = [i for i in self._G.nodes if 'h' in i]
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
        s,d = re.findall(r"\d+",k)
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


# links = {}
# with open(file) as fp:
#     for line in fp:
#         links[line.strip().split(' ')[0],line.strip().split(' ')[1]] = 0
# print(links)
# G_demo = get_graph('demotopo.txt')
G_fattree = get_graph('fattree.txt')
# G_irr = get_graph('irrgular.txt')
host_fattree = {'h1': '13', 'h2': '13', 'h3': '14', 'h4': '14', 'h5': '15', 'h6': '15', 'h7': '16',
                'h8': '16', 'h9': '17', 'h10': '17', 'h11': '18', 'h12': '18', 'h13': '19', 'h14': '19', 'h15': '20', 'h16': '20'}
# host_demo = {'h1': 1, 'h2': 2, 'h3': 4, 'h4': 5, 'h5': 7, 'h7': 8}
bw_fattree = {'(1,5)': 10, '(1,7)': 10, '(1,9)': 10, '(1,11)': 10, '(2,6)': 10, '(2,8)': 10, '(2,10)': 10, '(2,12)': 10,
              '(3,5)': 10, '(3,7)': 10, '(3,9)': 10, '(3,11)': 10, '(4,6)': 10, '(4,8)': 10, '(4,10)': 10, '(4,12)': 10,
              '(5,13)': 5, '(5,14)': 5, '(6,13)': 5, '(6,14)': 5, '(7,15)': 5, '(7,16)': 5, '(8,15)': 5, '(8,16)': 5,
              '(9,17)': 5, '(9,18)': 5, '(10,17)': 5, '(10,18)': 5, '(11,19)': 5, '(11,20)': 5, '(12,19)': 5,
              '(12,20)': 5}

if __name__ == '__main__':
    G = G_fattree
    Gb = Graphbasic(G)
    hosts = host_fattree
    bw = bw_fattree
    # part = community.best_partition(G)#community 分区方法
    # G =  nx.windmill_graph(4,5)
    # [counts,parts]=metis.part_graph(G,5)# metis 分区方法
    parts = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 1, 1, 2, 2, 3, 3, 4, 4]
    print(G.nodes)
    print(parts)
    ##路由分区绘图
    pos = nx.spring_layout(G)
    colors = ['red', 'blue', 'green', 'yellow', 'pink']
    value = []
    for i, p in enumerate(parts):
        value.append(colors[p])
    nx.draw_spring(G, cmap=plt.plot(), node_color=value
                   , node_size=100, with_labels=True)
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
    nx.draw_spring(G, node_size=100, with_labels=True)
    plt.show()

    ##计算端到端路径
    paths = Gb.getpath()
    print(paths)

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
    print(importance)

    set_importance = set()
    for i in importance.values():
        set_importance.add(i)
    importance = dict(sorted(importance.items(), key=lambda item: item[1], reverse=True))  # importance按值排序
    print(importance)

    ##待测路径比例
    r = 0.5
    probe = [k for k, v in importance.items()]
    probe = probe[16:]#只测pod里路径
    print(probe)

    find = 0  # 探测到的链路故障（故障发生在待测链路集上）
    miss = 0  # 故障发生在待测链路集外
    zfind = 0  # 探测到故障区域
    for i in range(1000):  # 进行1000个周期
        link = {}
        conf_link = {}
        fault_zone = [0] * len(parts)

        for i in swlinks:
            link[i] = 0
            conf_link[i] = False

        flow = genflow(hosts)
        print(flow)

        for k, v in flow.items():
            path = random.choice(paths['(%s,%s)' % (k[0], k[1])])
            for l in getpathlink(path, swlinks):
                # print(l)
                t = link[l]
                link[l] = t + v

        for k, v in link.items():
            if v > bw['(%s,%s)' % (int(k[0]), int(k[1]))]:
                t = faultrate[k]
                faultrate[k] = t + 1  # 链路故障次数
                conf_link[k] = True
        for k, v in conf_link.items():
            if v:
                if k in probe:
                    print(k)
                    print(re.findall(r"\d+", str(k)))
                    s, d = re.findall(r"\d+", str(k))  # 故障区域统计
                    fault_zone[parts[int(s) - 1]] = 1
                    fault_zone[parts[int(d) - 1]] = 1
                    find += 1
                    zfind += 1
                else:
                    miss += 1
                    s, d = re.findall(r"\d+", str(k))
                    if parts[int(s) - 1] == 1 and parts[int(d) - 1] == 1:
                        zfind += 1

    print(faultrate)
    print(find, miss, find / (miss + find), zfind, zfind / (miss + find))
    rate = 0
    sum = 0
    for k, v in importance.items():
        sum += v
        if k in probe:
            rate += v
    print(rate, sum - rate, rate / sum)