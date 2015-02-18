import json
import math
from collections import defaultdict
import urllib2
import pyorient

def connect():
	'''Function to connect to the database'''
	client = pyorient.OrientDB("localhost", 2424)
	session_id = client.connect( "root", "rootlabs" )
	client.db_open( "NetworkLabs", "admin", "admin")
	return client

def rad(x):
	'''Function to convert degree into radians'''
	return x * math.pi / 180

def get_distance(srclat, srclong, dstlat, dstlong):
	'''Function to calculate the Haversian distance between two geo locations'''
	#print "In the get distance function"
	R = 6378137L
	dLat = rad(dstlat - srclat)
	dLong = rad(dstlong - srclong)
	a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(srclat)) * math.cos(rad(dstlat)) * math.sin(dLong / 2) * math.sin(dLong / 2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	d = R * c
	return d

def get_duration(srclat, srclong, dstlat, dstlong):
	'''Function to calculate the walking time (in seconds) between two geo locations using Google APIs'''
	#print "In getDuration function"

	# Setting the Google Places API key
	AUTH_KEY = 'AIzaSyACzP9Vt7RxrLFqwsG4SkVGRIiSJC1kEWo'

	# Prepare the sourceLatLong and dstLatLong
	srcLatLong = str(srclat) + ',' + str(srclong)
	dstLatLong = str(dstlat) + ',' + str(dstlong)
	#print srcLatLong,dstLatLong

	# Compose a URL to query a predefined location with a radius of 5000 m
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + srcLatLong + "&destinations=" + dstLatLong + "&mode=walking"
	#print url

	# Send the GET request to the Place details service (using aove url)
	response = urllib2.urlopen(url)

	# Processing the response
	json_raw = response.read()
	json_data = json.loads(json_raw)
	#print json_data

	# Traverse the json to extract the time in seconds
	if json_data['status'] == 'OK':
		rows = json_data['rows'][0]
		elements = rows["elements"][0]
		duration = elements["duration"]
		time = duration["value"]
		# Return the time in seconds
		#print time
		return time
	else:
		# Couldnt find the distance - default to a large value
		print "Error",json_data['status']
        	return 99999

def rest_item_unpack(item):
	'''Function to unpack a pyorient item'''
	#print "Unpacking item"
	#'health_index' : "{0:.2f}".format(item.health_index*10) #incase we need health index

	return { 'res_id' : item.res_id, 'name' : item.name, 'address' : item.address, 'rating' : item.rating, 'latitude' : item.latitude, 'longitude' : item.longitude, 'mobile_url' : item.mobile_url, 'review_count' : item.review_count, 'cuisines' : item.cuisines, 'health_option' : item.health_option, 'image_url' : item.image_url, 'avg_price': item.avg_price }

def run_query(query='', srcLat='', srcLong='', distanceFlag=0):
	'''Function to run query and return the results'''
	print "Running the query and computing the results"

        # Converting lat long to floats
	if distanceFlag:
	        srcLat = float(srcLat)
        	srcLong = float(srcLong)

	# Creating a dictionary of dictionary to hold the results
	results = defaultdict(dict)

	# Create a client for connecting to the database
	client = connect()

	if query == '':
		# default query
		sql_query = "SELECT FROM Restaurant"
	else:
		sql_query = query

	# Run the query
	res = client.command(sql_query)
	print "Query executed successfully: " + sql_query

	# Iterating to construct the results dictionary.
        for item in res:
                # unpack the item
		results[item.rid] = rest_item_unpack(item)
		if distanceFlag:
			dstLat = float(item.latitude)
	                dstLong = float(item.longitude)
        	        # Accoding to the requirements can be changed
                	results[item.rid]['distance'] = get_distance(srcLat,srcLong,dstLat,dstLong)

	# return a dictionary of restaurant metadata
        return results

def get_constraints(uid):
	'''Function to get user constraints'''
	print "Getting Constraints for user", uid
	# Client to connect to database
	client = connect()

        res = client.command('SELECT from Person where @rid=#' + uid)
        return res[0].dollar_limit, res[0].time_limit

def checkin_search(srcLat='',srcLong=''):
	'''Function to provide restaurant options while checking in'''
	print "In checkin search API"
	# To display options for checkin there is no query, can be changed later if needed
	query = ''

	# Running query to fetch the results
	result = run_query(query, srcLat, srcLong, 1)
	result = sorted(result.values(), key=lambda x:int(x["distance"]))[:5]
	return result

def search_res(uid, query='', srcLat='', srcLong=''):
	'''Function that checks for all conditions and calls search with the right parameters'''
	print "In search API, checking for conditions and setting the flags"
	print uid, query, srcLat, srcLong

	# Checking for the different conditions
	if query == '':
		if srcLat == '' and srcLong == '':
			print "Query is empty and Location is turned off"
			result = search(uid, query, srcLat, srcLong, 0)
		else:
			print "Query is empty and Location is turned on"
			result = search(uid, query, srcLat, srcLong, 1)
	elif srcLat == '' and srcLong =='' :
		print "Query is not empty but location is turned off"
		result = search(uid, query, srcLAt, srcLong, 0)
	else:
		print "Query is not empty and Location is turned on"
		result = search(uid, query, srcLat, srcLong, 1)

	# Return the results
	return result

def get_max_walk_time(time_limit):
 	# checking time to set the appropriate max walk times
        if time_limit <= 30:
                max_walk_time = 5
        elif time_limit <= 45:
                max_walk_time = 10
        elif time_limit <= 60:
                max_walk_time = 15
        else:
                max_walk_time = 20

	return max_walk_time

def dist_item_unpack(res):
	# Create a dictionary to hold all distance - walk times
	temp = defaultdict()
	
	for item in res:
		temp[item.distance] = item.walk_time

	# return this dictionary
	return temp

def run_distance_query(result, max_walk_time):
	# to collect all distances
	distances_list = []

	for item in result:
		distances_list.append(result[item]["distance"])

	# query to get the corresponsing walking times in one go
	sql_query = "SELECT distance,walk_time FROM WalkingTimes where distance in " + str(distances_list) + " and walk_time<=" + str(max_walk_time)
	
	# Create a client for connecting to the database
	client = connect()

        # Run the query
        res = client.command(sql_query)
        print "Query executed successfully: " + sql_query

	# Store the unpacked result in a dictionary
	distances_hash = dist_item_unpack(res)
	
	for item in result:
		# Get the distance of the current object
		distance = int(result[item]['distance'])
		
		# Get the corresponding walking time and store it in our result dictionary
		result[item]['walk_time'] = distances_hash[distance]

	# return the result back which now has walking times as well
	return result

def search(uid, query='', srcLat='', srcLong='', distanceFlag=0):
	'''Function to search based on the parameters sent'''
	print "Search has been called with the appropriate parameters"

	# obtain the user constraints
	dollar_limit, time_limit = get_constraints(uid)
	#print dollar_limit, time_limit

	# obtain the max time based on user specification and convert to seconds
	max_walk_time = get_max_walk_time(time_limit) * 60.0

	# hash the co-ordinated if present to the grid and get the walking times
	if srcLat != '' and srcLong != '':
		walking_times = get_walking_times(srcLat,srcLong)

	if query == '':
		sql_query = "SELECT FROM Restaurant where avg_price<=" + str(dollar_limit)
	else:
		sql_query = "SELECT FROM Restaurant WHERE cuisines LIKE " + "\'%" +query.lower() + "%\'" + " OR name LIKE " + "\'%" + query.title() + "%\'" + " OR address LIKE " + "\'%" + query.title() + "%\'" + "and avg_price<=" + str(dollar_limit)

	# Running query to fetch the results
	result = run_query(sql_query, srcLat, srcLong, distanceFlag)

	# Sort by distance when the user geo location is present, else sort by the health options
	if distanceFlag:
		# pruning over max walking time here.
		result = run_distance_query(result, max_walk_time)
		result = sorted(result.values(), key=lambda x:int(x["walk_time"]))[:5]
	else:
		result = sorted(result.values(), key=lambda x:int(x["health_option"]), reverse=True)[:5]
	print "Finished sorting to the obtain top 5 results"

	# Compute the walking time when we have user geo location
	if srcLat != '' and srcLong != '':
		for item in result:
        	        dstLat = item['latitude']
                	dstLong = item['longitude']
	                walking_time = float(get_duration(srcLat, srcLong,dstLat, dstLong)) / 60.0
        	        item['walking_time'] = math.ceil(walking_time)
	print "Finished computing walking time for the top 5 results"

	# Return the top results
	return result
