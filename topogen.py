import networkx as nx

with open('ba50.txt','w') as fp:
    G_ba50 = nx.barabasi_albert_graph(50,2)
    for i in G_ba50.edges:
        fp.write(str(i[0])+' ')
        fp.write(str(i[1])+'\n')
    fp.close()


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