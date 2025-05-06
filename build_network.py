import os
import csv
import networkx as nx
from collections import defaultdict

folder = "Exports/"

network = nx.Graph()

nodes = {}
edges = defaultdict(int)

for file in os.listdir(folder):
    name = file.split("_")[0]
    nodes[name] = ("", "")

    similars = csv.reader(open(folder + file, 'r'))
    for similar in similars:
        genres = similar[2].split(",")
        nodes[similar[0]] = (similar[1], genres)
        edges[(name, similar[0])] += 1

network.add_nodes_from(nodes)
network.add_edges_from(edges)
print(network.number_of_nodes())
print(network.number_of_edges())
nx.write_gexf(network, "network.gexf")
