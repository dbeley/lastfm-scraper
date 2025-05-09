import os
import csv
import time
import networkx as nx
from pathlib import Path
from collections import defaultdict

# default folder for similar artists data
folder = "Exports_sample/"

# create graph object and nodes/edges lists
network = nx.Graph()
nodes = {}
edges = defaultdict(int)

# process files exported from the similar artists script
for file in os.listdir(folder):
    name = file.split("_")[0]
    nodes[name] = ("", "")
    similars = csv.reader(open(folder + file, 'r'))
    for similar in similars:
        listens = int(similar[1])
        genres = similar[2].split(",")
        if listens < 300000 and ("punk" in genres or "punk rock" in genres):
            nodes[similar[0]] = (listens, genres)
            edges[(name, similar[0])] += 1

# add nodes and edges to the networkx graph object
for node in nodes:
    if nodes[node][0] != '' and nodes[node][1] != '':
        network.add_node(node, size=nodes[node][0], genre_1=nodes[node][1][0])
    else:
        network.add_node(node)
for edge in edges:
    network.add_edge(edge[0], edge[1], weight=int(edges[edge]))

# print basic informations and write graph to .gexf file
print("The output network has :")
print("\t" + str(network.number_of_nodes()) + " nodes")
print("\t" + str(network.number_of_edges()) + " edges")

# outputs gexf file to a subdirectory
Path("Networks").mkdir(parents=True, exist_ok=True)
timestr = time.strftime("%Y%m%d-%H%M%S")
nx.write_gexf(network, "Networks/" + timestr + "_network.gexf")
