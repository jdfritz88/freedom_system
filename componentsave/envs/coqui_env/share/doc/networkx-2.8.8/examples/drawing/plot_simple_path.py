import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
"""
===========
Simple Path
===========

Draw a graph with matplotlib.
"""
import matplotlib.pyplot as plt
import networkx as nx

G = nx.path_graph(8)
pos = nx.spring_layout(G, seed=47)  # Seed layout for reproducibility
nx.draw(G, pos=pos)
plt.show()
