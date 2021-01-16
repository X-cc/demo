import faultrate as fr
import networkx as nx
import matplotlib.pyplot as plt

if __name__ == '__main__':
    G = fr.G_irr
    Gb = fr.Gb
    probe = fr.probe[:]
    paths = fr.paths
    hosts = fr.hosts
    swlinks = fr.swlinks

    fp = open('probe_paths.json','w')
    probe_paths = {}
    probe_links = []
    while len(probe)!=0:
        max = []
        probe_path = []
        probe_sd = None
        for k,v in paths.items():
            for i in v:
                path_links =  fr.getpathlink(i,swlinks)
                # print(path_links)
                # print(probe)
                tmp =  [i for i in probe if i in path_links]
                # print(tmp)
                if len(tmp)>len(max):
                    print(tmp)
                    max = tmp
                    probe_path = i
                    probe_sd = k

        # print(probe_path)
        probe_paths[probe_sd] = probe_path
        probe_links += fr.getpathlink(probe_path,swlinks)
        for i in max:
            probe.remove(i)
    print('probe_paths',probe_paths)
    print('probe',fr.probe)
    print('probe_links',probe_links)


    for e in G.edges:
        # print(e)
        G[e[0]][e[1]]['color'] = 'grey'
    # Set color of edges of the shortest path to green
    for i in probe_links:
        G[i[0]][i[1]]['color'] = 'red'
    # Store in a list to use for drawing
    edge_color_list = [G[e[0]][e[1]]['color'] for e in G.edges()]
    node_color_list = fr.color_value
    for i in range(len(G.nodes)-len(fr.color_value)):##为host上色
        node_color_list.append('white')
    nx.draw(G, node_color=node_color_list, edge_color=edge_color_list, with_labels=True)
    plt.show()






