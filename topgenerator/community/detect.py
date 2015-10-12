#Copyright (c) 2015 Crowd Dynamics Labs
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import community
import networkx as nx
import matplotlib.pyplot as plt
import pyorient
import numpy as np
import math

def generate_cluster_graph(n,m,in_p,out_p):
	'''Generates graph with 'n' nodes with form m clustures,
	with average in_p within cluster and 'out_degree' between clustures'''
	print "Generating G..."
	if m == 0 or n == 0:
		raise "n or m can not be 0"

	nodes_per_clusture = n/m
	num_of_outer_nodes = math.ceil(nodes_per_clusture * out_p)
	larger_graph = nx.Graph()
	print "\tExpected communities:",m
	print "\tnodes_per_clusture:",nodes_per_clusture,"\n\tnum_of_outer_nodes:",num_of_outer_nodes
	for i in xrange(m):
		# print 'clusture_id',i
		G = nx.fast_gnp_random_graph(nodes_per_clusture,in_p)
		for node in G.nodes():
			larger_graph.add_node((node)+nodes_per_clusture*i)
		for edge in G.edges():
			larger_graph.add_edge((edge[0])+nodes_per_clusture*i,(edge[1])+nodes_per_clusture*i)
		
		chosen_nodes = np.random.choice(G.nodes(),num_of_outer_nodes)
		for node in chosen_nodes:
			node_for_large_graph = node+nodes_per_clusture*i
			larger_graph.add_edge(node_for_large_graph,np.random.choice(larger_graph.nodes()))
	# print larger_graph.nodes()
	# print larger_graph.edges()
	return larger_graph


def get_server_network():
	cl = pyorient.OrientDB("localhost", 2424)
	session_id = cl.connect( "root", "rootlabs" )
	cl.db_open( "NetworkLabs", "admin", "admin")

	users = cl.command('select from Person')
	graph = nx.Graph()

	for u in users:
		rid = u.rid
		name = u.first_name+' '+u.last_name
		graph.add_node(rid)

	friend_edges = cl.command('select from friends_with')
	for edge in friend_edges:
		in_node = '#'+edge._in.clusterID+':'+edge._in.recordPosition
		out_node = '#'+edge._out.clusterID+':'+edge._out.recordPosition
		graph.add_edge(in_node,out_node)


def detect_com(G):
	print "Performing community detection..."
	#first compute the best partition
	partition = community.best_partition(G)
	# print partition
	#drawing
	size = float(len(set(partition.values())))
	print '\tDetected communities:',size
	print "Drawing graph..."
	print "\tPositioning nodes on layout..."
	pos = nx.spring_layout(G)
	node_colors = ['r','g','b','c','m','y','k','w']
	count = 0
	print "\tDrawing nodes..."
	for com in set(partition.values()) :
	    list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
	    nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20, node_color = node_colors[count])
	    count+=1
	print "\tDrawing edges..."
	nx.draw_networkx_edges(G,pos, alpha=0.5)
	plt.savefig('community_fig.png')

if __name__ == '__main__':
	G = generate_cluster_graph(1000,8,0.7,0.9)
	detect_com(G)
