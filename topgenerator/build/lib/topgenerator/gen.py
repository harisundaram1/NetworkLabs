import snap
import csv
import random
from .connect_db import *
from pyorient.utils import *
import re
import math
import numpy as np
import datetime
import os
import base64
# INPUT:
#	-	100 user names
#	-	5 actions
#	-	Type of network, Eg.: "small_world", "random"
#	-	Probabilty p
# OUTPUT:
#	1. Read the input and create array of users and create an list.
#	2. Each array intex is the node index in snap graph
#	3. Create a graph with given input network type and probability p.
#	4. Using the snap graph, create the edge
#	5. Save the graph
################################################################################################################
OUT_DEG = 2
LINK_PROB = 0.1
ADD_INFO_NETWORK = False
RANDOM_INFO_EDGE_COUNT = 1
################################################################################################################

def get_info_edges(graph,node_id,edge_count=2):
	return
	node_count = graph.GetNodes()
	for i in xrange(edge_count):
		out_node = graph.GetRndNId()
		while out_node == node_id or graph.IsEdge(out_node,node_id):
			out_node = graph.GetRndNId()
		graph.AddEdge(node_id,outnode)

def get_all_cuisines(restaurants):
	all_cuisines = []
	for res in restaurants:
		all_cuisines.extend(res['cuisines'])
	all_cuisines = set(all_cuisines)
	return all_cuisines

def get_users(count=10):
	# Generating users from the CSV list
	users = []
	all_cuisines = get_all_cuisines(get_restaurants())
	users = get_data('random_users_plus5.csv')
	for user in users:
		# Add prob_of_activity
		user['prob_of_activity'] = round(random.uniform(0,0.5),4)
		user['prob_of_comment'] = round(random.uniform(0,0.7),4)
		user['prob_of_like'] = round(random.uniform(0,1),4)
		# Add 2 random cuisines
		user['cuisines_liked'] = random.sample(all_cuisines,2)
		if user['email'] == '':
			user['email'] = user['first_name'].lower()+user['last_name'].lower()+'@illinois.edu'
		user['ethnicity'] = np.random.choice(['Martian','Vulcan','Human','Romulan','Klingon'],1)[0]
		user['age'] = int(random.uniform(17,30))

	return users[0:count]

def get_restaurants():
	# Get restaurants from the Yelp dataset
	restaurants = get_data('restaurant_data_nov3_v2.csv')
	filtered_list = []
	for res in restaurants:
		if re.search('Urbana|Champaign',res['address']):
			# print res['res_id']
			# res['cuisines'] = re.findall(r"[\w']+", res['cuisines'])
			res['rating'] = float(res['rating'])
			res['review_count'] = int(res['review_count'])
			res['latitude'] = float(res['latitude'])
			res['longitude'] = float(res['longitude'])
			filtered_list.append(res)
	return filtered_list

def get_data(filename):
	data_list = []
	with open('data/'+filename,mode='rU') as datafile:
		reader = csv.reader(datafile)
   		data_item = {}
   		headers = reader.next()
   		for row in reader:
   			# print  row
   			data_item = {headers[i]:row[i] for i in xrange(len(headers))}
   			data_list.append(data_item);
   	return data_list

def get_prob():
	return random.random()

def get_friends_count():
	return OUT_DEG

def add_info_network(graph):
	# For given graph, for each node, add a random information network, such that it is not a self loop or repeated edge
	for ni in graph.Nodes():
		out_edge_nodes = get_info_edges(graph,ni,RANDOM_INFO_EDGE_COUNT)

def save_graph_in_db(graph):
	# for each node, prepare transaction and commit.
	# for each edge, loop the result and create edge.
	# node[#cluster:index]
	users = get_users(graph.GetNodes())
	cl = connect()
	temp_rec = cl.command('Create vertex Person set name="Ford",email="Prefect"')
	cluster_id = int(parse_cluster_id(temp_rec[0].rid))
	cl.record_delete(cluster_id,temp_rec[0].rid)
	# print "cluster_id: "+str(cluster_id)
	for u in users:
		rec = {'@Person': u}
		res_rec = cl.record_create(cluster_id,u)
	#get all nodes
	nodes = cl.command('select from Person limit '+str(len(users)))
	# print nodes
	for edge in graph.Edges():
		res_rec = cl.command('create edge friends_with from '+str(nodes[edge.GetSrcNId()].rid)+' to '+str(nodes[edge.GetDstNId()].rid))
		# print str(nodes[edge.GetSrcNId()].rid)+'-'+str(nodes[edge.GetDstNId()].rid)
	create_custom_fiends()

def create_users_network(user_count=10,friends_count=get_friends_count(),prob=get_prob(),network_type='random',conf_model=False):
	# User list, probability p and network_type is given, construct a graph
	res ="empty"
	
	# generate specific graphs
	if network_type.lower().find("small") >=0:
		# This is a small world network
		print "Creating a small world network with "+str(user_count)+" users"
		rnd = snap.TRnd(1,0)
		new_graph = snap.GenSmallWorld(user_count,friends_count,prob, rnd)
	elif network_type.lower().find("ring") >=0:
		# A ring graph
		print "Creating a ring with "+str(user_count)+" users"
		new_graph = snap.GenCircle(snap.PUNGraph,user_count,friends_count)
	elif network_type.lower().find("power") >=0:
		# Power Law network
		print "Creating a powerlaw network with "+str(user_count)+" users"
		new_graph = snap.GenRndPowerLaw(user_count,friends_count,conf_model)
	else:
		# A random graph
		print "Creating a random network with "+str(user_count)+" users"
		edge_count = user_count*friends_count
		new_graph = snap.GenRndGnm(snap.PUNGraph,user_count,edge_count)
	# Add info network if required
	if ADD_INFO_NETWORK:
		add_info_network(new_graph)

	#save the graph in DB
	save_graph_in_db(new_graph)

def create_restaurants():
	client = connect()
	restaurants = get_restaurants()
	temp_rec = client.command('Create vertex Restaurant set name="Restaurant at the End of the Universe", res_id="42"')
	cluster_id = int(parse_cluster_id(temp_rec[0].rid))
	client.record_delete(cluster_id,temp_rec[0].rid)

	for res in restaurants:
		rec = {'@Restaurant': res}
		# print rec
		res_rec = client.record_create(cluster_id,res)

def clear_network():
	# deletes all nodes and edges
	cl = connect()
	print "Deleting all Nodes and Edges"
	cl.command('delete from V')
	cl.command('delete from E')

# def create_activities(users,activity_count,datetime):
# 	# Given a set of users and total activity count
# 	# For each user , get the number of act of activities to be created depeding on the activeness
# 	cl = connect()
# 	activities = []
# 	print 'Creating '+str(activity_count)+' activities'
# 	for user in users:
# 		activities_to_create = int(math.ceil(user.prob_of_activity*activity_count))
# 		# print activities_to_create
# 		restaurants = cl.command('select * from Restaurant where cuisines in '+str(user.cuisines_liked)+' limit 100')
# 		try:
# 			restaurants = random.sample(restaurants,activities_to_create) 
# 		except Exception, e:
# 			# Number of restaurants is less than number of activities.
# 			# Fetch more restaurants
# 			temp_res = cl.command('select * from Restaurant where cuisines in '+str(user.cuisines_liked)+' limit '+str(activities_to_create-len(restaurants)))
# 			restaurants.extend(temp_res)
# 		for res in restaurants:
# 			activities.append({'user_id':user.rid,'user_name':user.name,'restaurant_id':res.rid,'restaurant_name':res.name})
# 	# Insert activities
# 	# print activities
# 	for act in activities:
# 		# print act
# 		act_string = 'create vertex Action set type="Eat"'#,created_at="'+datetime+'"'
# 		print act_string
# 		act_rec = cl.command(act_string)
# 		cl.command('create edge performs from '+str(act['user_id'])+' to '+str(act_rec[0].rid))
# 		cl.command('create edge at from '+str(act_rec[0].rid)+' to '+str(act['restaurant_id']))
# 		print ''+str(act['user_name'])+' ate at '+str(act['restaurant_name'])+' on '+datetime

def similar_user(user,constraint,user_count):
	cl = connect()
	str_cmd = 'select from Person where '+constraint+' contains (select '+constraint+' from Person where @rid in '+str(user.rid)+') limit '+str(user_count)
	print str_cmd
	users = cl.command(str_cmd)
	return users

def get_count_given_probability(p=0):
	# Here given a probability we return count
	# Init: count = 0
	# Generate a uniform random number r
	# if r < p ? count++ : return count
	count = 0
	r = 0
	while r<p and p<1:
		count+=1
		r = random.uniform(0,1)
	return count

def get_activities_probs_for_user(user):
	# return set of 4 probabilities - > psi, gamma, alpha, beta such that sum is 1
	# read from user if required
	return [0.25,0.25,0.25,0.25]

def get_prob_index(probability_list):
	# Given a list of probabilities, pick a probability
	return np.random.choice([0,1,2,3],1,probability_list)[0]
def get_own_activity(user, k=10):
	# Get a restaurant that a user has visited after the visit_date
	cl = connect()
	restaurants = cl.command('Select expand(out("performs").out()) from Person where @rid="'+user.rid+'"')
	if len(restaurants) == 0:
		restaurants = get_new_activity(user)
	return random.sample(restaurants,1)

def get_friends_activity(user, k=10):
	# Get a restaurant that a user's friend has visited after the visit_date
	cl = connect()
	cmd_str = "select from Restaurant where @rid in ( select in from eats_at where out in (select expand(both('friends_with').@rid) from Person where @rid="+user.rid+") order by created_at desc limit "+str(k)+")"
	# print cmd_str
	restaurants = cl.command(cmd_str)
	if len(restaurants) == 0:
		restaurants = get_new_activity(user)
	return random.sample(restaurants,1)

def get_background_dist_activity(user, k=10):
	# Get a restaurant that anyone in the network has visited after the visit_date
	cl = connect()
	cmd_str = 'select from Restaurant where @rid in (select in from eats_at order by created_at desc limit '+str(k)+')'
	# print cmd_str
	restaurants = cl.command(cmd_str)
	if len(restaurants) == 0:
		restaurants = get_new_activity(user)
	return random.sample(restaurants,1)

def get_new_activity(user):
	# Create a new activity for the user.
	cl = connect()
	known_rests = []
	# print user.rid
	own_rests = cl.command('Select expand(out("eats_at")) from Person where @rid='+user.rid)
	cmd_str  = 'Select expand(both("friends_with").out("eats_at")) from Person where  @rid='+user.rid
	# print cmd_str
	friends_rests = cl.command(cmd_str)
	# print len(friends_rests)
	known_rests.extend(own_rests)
	known_rests.extend(friends_rests)
	rest_rids = set()
	for rest in known_rests:
		rest_rids.add(rest.rid)
	# print str(list(rest_rids))
	# print len(rest_rids)
	cmd_str = 'Select from Restaurant where @rid not in '+str(list(rest_rids)).replace("'","")
	# print cmd_str
	new_rests = cl.command(cmd_str)
	# print len(new_rests)
	return np.random.choice(new_rests,1)

def get_restaurants_for_activities(user):
	# Get no of activitis to perform for the user with  probability = prob_of_activity
	# Define psi, gamma, alpha, beta for the user such that sum is 1
	# psi ->  activity from user's own activity history
	# gamma -> activity from user's friend's activity history
	# alpha -> activity from background i.e all
	# beta -> new activity
	# Run the algo n times where n is the activities count
	# Pick a probability for picking rest
	# print 'generating activity for user '+user.first_name+' '+user.last_name
	activities_count = get_count_given_probability(user.prob_of_activity)
	# print 'performing count '+str(activities_count)
	activities_probabilities = get_activities_probs_for_user(user)
	restaurant_list = []
	for act in xrange(0,activities_count):
		prob_index = get_prob_index(activities_probabilities)
		if prob_index == 0:
			# psi
			# print 'own history'
			restaurant_list.extend(get_own_activity(user))
		elif prob_index == 1:
			# gamma
			# print 'friends history'
			restaurant_list.extend(get_friends_activity(user))
		elif prob_index == 2:
			# alpha
			# print 'background distribution'
			restaurant_list.extend(get_background_dist_activity(user))
		elif prob_index == 3:
			# beta
			# print 'new activity'
			restaurant_list.extend(get_new_activity(user))
	return restaurant_list

def create_activity_cards(users,creation_date=datetime.date.today()):
	restaurant_list = []
	card_list = []
	cl = connect()
	for user in users:
		restaurant_list = get_restaurants_for_activities(user)
		for restaurant in restaurant_list:
			print user.first_name+' eats at '+restaurant.name+' on '+creation_date.strftime('%Y-%m-%d')
			cmd_str = 'create edge eats_at from '+user.rid+' to '+restaurant.rid+' set created_at ="'+creation_date.strftime('%Y-%m-%d')+'"'
			# print cmd_str
			cl.command(cmd_str)
			card_list.append({'user':user,'rest':restaurant,'date':creation_date})
	create_card(card_list)

def get_random_food_picture():
	cl = connect()
	images = cl.command('select from BinaryData')
	p = random.random()
	if p > 0.5:
		res = random.sample(images,1)[0].rid
	else:
		res = ''
	return res

def create_card(card_list=[]):
	cl = connect()
	print 'Need to create '+str(len(card_list))+' cards'
	for card in card_list:
		print 'inserting card '+str(card_list.index(card)+1)
		image_id = get_random_food_picture()
		# print image_id
		cmd_str = 'create vertex Card set comment_count=0\
					,comment_list=[]\
					,created_at_datetime="'+card['date'].strftime('%Y-%m-%d')+'"\
					,like_count=0\
					,like_list=[]\
					,location={}\
					,people_involved=[]\
					,location_name="'+card['rest'].name+'"\
					,text="Eating at '+card['rest'].name+'"\
					,type="Eat"\
					,created_at="'+str(int(card['date'].strftime('%s'))*1000)+'"\
					,first_name="'+card['user'].first_name+'"\
					,last_name="'+card['user'].last_name+'"\
					,image='+image_id
		# print cmd_str
		card_record = cl.command(cmd_str)
		friends = []
		friends = cl.command('select expand(both("friends_with")) from Person where @rid='+card['user'].rid)
		friends.extend(cl.command('select expand(in("follows")) from Person where @rid='+card['user'].rid))
		if len(card_record) >0:
			rec_id = card_record[0].rid
			cl.command('create edge at from '+rec_id+' to '+card['rest'].rid)
			cl.command('create edge creates from '+card['user'].rid+' to '+rec_id)
			for friend in friends:
				cl.command('create edge can_view from '+friend.rid+' to '+rec_id)

def get_restaurant_vector(user):
	# Create a vector for given user
	# such that v_i is the i'th value of vector for restaurant i, where value is count of visit.
	rest_vector = []
	cl=connect()
	restaurants = cl.command('select from Restaurant order by @rid asc')
	for rest in restaurants:
		# print rest.rid
		rest_vector.append(cl.command('select count(*) from eats_at where in='+rest.rid+' and out='+user.rid)[0].count)
	# print rest_vector
	return np.array(rest_vector)

def cosine_similarity(u, v): 
		return np.dot(u, v) / (np.sqrt(np.dot(v1, v1)) * np.sqrt(np.dot(v2, v2))) 

def get_cosine_similarity(u,v):
	# For user u and v, create vector 
	# perform cosine similarity
	# return value
	# use different feature for vector creation. 
	# Firstly use restaurants
	similarity = 0
	vector_u = get_restaurant_vector(u)
	vector_v = get_restaurant_vector(v)

def get_exception_users():
	cl = connect()
	users = cl.command('Select from Person where first_name in ["Pranav","Cheng Han","Balachander","Sanjana","Hari"]')
	return users

def get_exception_user_rid():
	users = get_exception_users()
	rids = [u.rid for u in users]
	return rids

def create_custom_fiends():
	# Create custom friendships between users
	cl = connect()
	users = get_exception_users()
	for i in xrange(0,len(users)):
		for j in xrange(i+1,len(users)):
			in_count = cl.command('select count(*) from friends_with where in='+users[i].rid+' and out='+users[j].rid)[0].count
			out_count = cl.command('select count(*) from friends_with where in='+users[j].rid+' and out='+users[i].rid)[0].count
			if in_count==0 and out_count==0:
				cl.command('create edge friends_with from '+users[i].rid+' to '+users[j].rid)
				print 'Created friends_with edge from '+users[i].first_name+' to '+users[j].first_name

def create_binary_data():
	print 'saving the food images as nodes'
	cl = connect()
	file_names = []
	for f in os.listdir('data/img'):
		if re.search('jpg|jpeg|png',f):
			file_names.append(f)
	# print file_names
	for fl in file_names:
		print 'creating node for image '+fl
		with open('data/img/'+fl,mode='rd') as img_file:
			encoded_str = base64.b64encode(img_file.read())
		cl.command('create vertex BinaryData set data="'+encoded_str+'"')





