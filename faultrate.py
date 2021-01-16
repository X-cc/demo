import networkx as nx
import random
import matplotlib.pyplot as plt
import community
import metis
import re


def get_graph(file):
    G = nx.Graph()
    with open(file) as text:
        for line in text:
            vertices = line.strip().split(" ")
            source = vertices[0]
            if "e" in source:
                break
            target = vertices[1]
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


    def getpath(self):
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

def getprobepath(probe,paths,swlinks):
    probe_station = set()
    probe_paths = {}
    probe_links = []
    while len(probe)!=0:
        max = []
        probe_path = []
        probe_sd = None
        cost = 0
        for k,v in paths.items():
            for i in v:
                path_links =  getpathlink(i,swlinks)
                # print(path_links)
                # print(probe)
                tmp =  [i for i in probe if i in path_links]
                if len(tmp)==0:
                    continue
                else:
                    tmp_cost = len(tmp)/len(path_links)+2#计算代价，+2是两端点代价
                    # print(tmp)
                    # if len(tmp)>len(max):
                    if tmp_cost>cost:
                        cost = tmp_cost
                        # print(tmp)
                        max = tmp
                        probe_path = i
                        probe_sd = k

        # print(probe_path)
        s,d = re.findall(r"\d+",probe_sd)
        print(s,d)
        probe_station.add(s)
        probe_station.add(d)
        probe_paths[probe_sd] = probe_path
        probe_links += getpathlink(probe_path,swlinks)
        for i in max:
            probe.remove(i)
    return probe_paths,probe_links,probe_station

G_demo = get_graph('demotopo.txt')
G_irr = get_graph('irrgular.txt')

host_demo = {'h1':'1','h2':'2','h3':'4','h4':'5','h5':'7','h6':'8'}
bw_demo = {'(1,2)':3,'(1.3)':3,'(2,3)':3,'(3,4)':4,'(3,5)':5,'(4,6)':10,'(5,7)':10,'(6,7)':3,'(6,8)':3,'(7,8)':3}
host_irr = {'h1':'1','h2':'2','h3':'3','h4':'5','h5':'7','h6':'8','h7':'9'}
bw_irr = {'(1,2)':5,'(1,4)':3.5,'(1,5)':5,'(2,3)':9,'(2,4)':6,'(3,4)':7,'(3,7)':5,'(3,8)':4.5,'(4,6)':7,'(4,7)':5,'(5,6)':6,'(6,7)':2.5,'(6,8)':8,'(8,9)':7}


###实验初始化
G = G_irr
Gb = Graphbasic(G)
hosts = host_irr
bw = bw_irr
# part = community.best_partition(G)#community 分区方法
# G =  nx.windmill_graph(4,5)
[counts,parts]=metis.part_graph(G,5)# metis 分区方法

print(G.nodes)
print(parts)
##路由分区绘图
pos = nx.spring_layout(G)
colors = ['red', 'blue', 'green', 'yellow', 'pink']
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
importance = dict(sorted(importance.items(), key=lambda item:item[1], reverse=True)) # importance按值排序
print(importance)

##待测路径比例
r = 0.5
probe = [k for k,v in importance.items()]
probe = probe[0:int(len(probe)*r)]
print(probe)
probe_paths,probe_links,probe_station = getprobepath(probe[:],paths,swlinks)
print('probe',probe)
print('probe_paths',probe_paths)
print('probe_links',probe_links)
for e in G.edges:
    # print(e)
    G[e[0]][e[1]]['color'] = 'grey'
# Set color of edges of the shortest path to green
for i in probe_links:
    G[i[0]][i[1]]['color'] = 'red'
# Store in a list to use for drawing
edge_color_list = [G[e[0]][e[1]]['color'] for e in G.edges()]
node_color_list = color_value
for i in range(len(G.nodes) - len(color_value)):  ##为host上色
    node_color_list.append('white')
nx.draw(G, node_color=node_color_list, edge_color=edge_color_list, with_labels=True)
plt.show()
if __name__=='__main__':
    find = 0#探测到的链路故障（故障发生在待测路径集上）
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
            if v > bw['(%s,%s)'%(int(k[0]),int(k[1]))]:
                t = faultrate[k]
                faultrate[k] = t+1 #链路故障次数
                conf_link[k] =True
        # print(conf_link)
        for k,v in conf_link.items():
            miss_link = []
            if v :
                if k in probe_links:
                    s,d = re.findall(r"\d+",str(k))#故障区域统计
                    fault_part[parts[int(s)-1]] = 1
                    fault_part[parts[int(d)-1]] = 1
                    find += 1
                    zfind += 1
                else:
                    miss_link.append(k)
                    miss += 1


            if len(miss_link)!=0:
                snode = []#可疑区域节点
                for i,p in enumerate(fault_part):
                    if p == 1:
                        for j,part in enumerate(parts):
                            if part==i:
                                snode.append(str(j+1))
                print(snode)
                G_sub= G.subgraph(list(snode))#可疑节点子图
                sub_edges = G_sub.edges()-list(i for i in probe_links)#已探测
                measure_links = 
                for i in sub_edges:

                nx.draw(G_sub)
                plt.show()
                print(fault_part)
                print(miss_link)
                for k in miss_link:
                    s, d = re.findall(r"\d+", str(k))
                    print(parts[int(s)-1], parts[int(d)-1])
                    print(fault_part[parts[int(s)-1]], fault_part[parts[int(d)-1]] )
                    ##假设发现待测链路故障就一定能发现该故障区域内故障
                    if fault_part[parts[int(s)-1]] == 1 or fault_part[parts[int(d)-1]] == 1:
                        zfind += 1


    print(faultrate)
    print('待测链路集检出异常数：',find,'漏检异常数：', miss,'待测路径检测率：', find / (miss+find),'区域故障检出数：',zfind,'区域故障检出率:',zfind/(miss+find))
    rate = 0
    sum = 0
    for k,v in importance.items():
        sum+=v
        if k in probe_links:
            rate+=v
    print('待测链路重要度和:',rate,'总重要度和：',sum-rate,'待测链路集重要度占比：',rate/sum)
    print('待测链路数：',len(probe),'探针覆盖链路数：',len(probe_links),'总链路数：',len(swlinks),'测量覆盖率：',len(probe_links)/len(swlinks),'探测路径条数：',len(probe_paths))
    print('探针站数：',len(probe_station),'探针站部署代价：',len(probe_station)/len(hosts))

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