import os
import csv

folder = "Exports/"

network = csv.writer(open("network.csv", 'w'))

for file in os.listdir(folder):
    name = file.split("_")[0]
    similars = open(folder + file).readlines()
    similars = ','.join([x.strip() for x in similars])
    newline = [name, similars]
    network.writerow(newline)
