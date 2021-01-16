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

def getprobepath(probe,paths,swlinks):
    probe_paths = {}
    probe_links = []
    probe_station =set()
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

G_random_geo= nx.random_geometric_graph(100,0.2)
G_ba50 = get_graph('ba50.txt')
G_ba50_host_30 = {'h1': 23, 'h2': 45, 'h3': 41, 'h4': 21, 'h5': 22, 'h6': 48, 'h7': 44, 'h8': 11, 'h9': 43, 'h10': 36, 'h11': 8, 'h12': 5, 'h13': 2, 'h14': 34, 'h15': 20}
G_ba100= get_graph('ba100.txt')
G_ba200= get_graph('ba200.txt')
G_ba300= get_graph('ba300.txt')
G_ba400= get_graph('ba400.txt')
G_ba100_host_30 = {'h1': 84, 'h2': 15, 'h3': 68, 'h4': 29, 'h5': 60, 'h6': 59, 'h7': 96, 'h8': 72, 'h9': 93, 'h10': 78, 'h11': 19, 'h12': 52, 'h13': 11, 'h14': 58, 'h15': 37, 'h16': 77, 'h17': 64, 'h18': 3, 'h19': 28, 'h20': 4, 'h21': 86, 'h22': 13, 'h23': 88, 'h24': 53, 'h25': 67, 'h26': 18, 'h27': 61, 'h28': 62, 'h29': 81, 'h30': 80}
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

    ##按待测路径比例r选出待测路径
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
    print('all_link_probe_station', all_link_probe_station)
    for e in G.edges:
        # print(e)
        G[e[0]][e[1]]['color'] = 'grey'
    # Set color of edges of the shortest path to green
    for i in probe_links:
        G[i[0]][i[1]]['color'] = 'red'
    # Store in a list to use for drawing
    edge_color_list = [G[e[0]][e[1]]['color'] for e in G.edges()]
    node_color_list = color_value
    for i in range(len(G.nodes)-len(color_value)):##为host上色
        node_color_list.append('white')
    nx.draw(G, node_size=100,node_color=node_color_list, edge_color=edge_color_list, with_labels=True)
    plt.show()

    finds = []
    misses = []
    zfinds = []

    for i in range(10):
        find = 0#探测到的链路故障（故障发生在待测链路集上）
        miss = 0#故障发生在待测链路集外
        zfind = 0#探测到故障区域

        for i in range(1000):#进行1000个周期
            link = {}
            conf_link = {}
            fault_part = [0]*(max(parts)+1)

            for i in swlinks:
                link[i] = 0
                conf_link[i] = False

            flow = genflow(hosts)
            # print(flow)

            for k,v in flow.items():
                path = random.choice(paths['(%s,%s)'%(k[0],k[1])])
                for l in getpathlink(path,swlinks):
                    # print(l)
                    t = link[l]
                    link[l] = t+v

            for k,v in link.items():
                if v > bw[(int(k[0]),int(k[1]))]:
                    t = faultrate[k]
                    faultrate[k] = t+1 #链路故障次数
                    conf_link[k] =True

            for k,v in conf_link.items():
                miss_link = []
                if v :
                    if k in probe_links:
                        # print(k)
                        # print(re.findall(r"\d+",str(k)))
                        s,d = re.findall(r"\d+",str(k))#故障区域统计
                        fault_part[parts[int(s)]] = 1
                        fault_part[parts[int(d)]] = 1
                        find += 1
                        zfind += 1
                    else:
                        miss_link.append(k)
                        miss += 1


                if len(miss_link)!=0:
                    for k in miss_link:
                        # print(fault_part)
                        # print(miss_link)
                        s,d = re.findall(r"\d+", str(k))
                        # print(parts[int(s)], parts[int(d)])
                        # print(fault_part[parts[int(s)]], fault_part[parts[int(d)]])
                        # print(fault_part[parts[int(s)]], fault_part[parts[int(d)]])
                        ##只要区域内有一个拥塞节点就再检测
                        if fault_part[parts[int(s)]]==1 and fault_part[parts[int(d)]]==1:
                            zfind += 1

        finds.append(find)
        misses.append(miss)
        zfinds.append(zfind)
        # print(faultrate)
        print('待测链路集检出异常数：', find, '漏检异常数：', miss, '待测路径检测率：', find / (miss + find), '区域故障检出数：', zfind, '区域故障检出率:',
              zfind / (miss + find))
    tmp = []
    tmp.append(finds)
    tmp.append(misses)
    tmp.append(zfinds)
    res = np.array(tmp)
    print(np.mean(res,axis=1))
    # print(finds)
    # print(misses)
    # print(zfinds)
    rate = 0
    sum = 0
    for k, v in importance.items():
        sum += v
        if k in probe_links:
            rate += v
    print('待测链路重要度和:', rate, '总重要度和：', sum , '待测链路集重要度占比：', rate / sum)
    print('待测链路数：', len(probe), '探针覆盖链路数：', len(probe_links), '总链路数：', len(swlinks), '测量覆盖率：',
          len(probe_links) / len(swlinks), '探测路径条数：', len(probe_paths))
    print('探针站数：', len(probe_station), '探针站部署代价：', len(probe_station) / len(hosts))
    print(set(parts),mpart)


    # print(ls)
    # plt.figure(dpi=80)
    # fig = plt.figure(figsize=(13, 11))
    #
    # ax1 = fig.add_subplot(2, 1, 1)
    # ax2 = fig.add_subplot(2, 1, 2)
    # plt.sca(ax1)
    # ax1.set_xticklabels(ls,fontsize=16,rotation=45)
    # avg = []
    # for i in faultrate.values():
    #     avg.append(i/1000)
    # plt.plot(ls,faultrate)
    # plt.sca(ax2)
    # ax2.set_xticklabels(ls,fontsize=16, rotation=45)
    # plt.plot(ls,list(linkrate.values()))
    # plt.plot(ls,avg)



    # plt.tight_layout()
    # plt.show()