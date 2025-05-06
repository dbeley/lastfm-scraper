import os
import csv
import networkx as nx
from collections import defaultdict

# default folder for similar artists data
folder = "Exports/"

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
        genres = similar[2].split(",")
        nodes[similar[0]] = (similar[1], genres)
        edges[(name, similar[0])] += 1

# add nodes and edges to the networkx graph object
for node in nodes:
    network.add_node(node, size=nodes[node][0], genres=nodes[node][1])
for edge in edges:
    network.add_edge(edge, weight=edges[edge])

# print basic informations and write graph to .gexf file
print("The output network has :")
print("\t" + str(network.number_of_nodes()) + " nodes")
print("\t" + str(network.number_of_edges()) + " edges")
nx.write_gexf(network, "network.gexf")
