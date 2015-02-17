import json
import math
from collections import defaultdict
import urllib2
import connect_db as db 

slat = 40.113824
slong = -88.207785
uid = 234
srcAddress = "201+North+Goodwin+Avenue+Urbana+IL+61801"

def connect():
	client = pyorient.OrientDB("localhost", 2424)
	session_id = client.connect( "root", "rootlabs" )
	client.db_open( "NetworkLabs", "admin", "admin")
	return client

def getDuration(dstAddress):
	# Setting the Google Places API key
	AUTH_KEY = 'AIzaSyACzP9Vt7RxrLFqwsG4SkVGRIiSJC1kEWo'
	# Prepare the sourceLatLong and dstLatLong
	#srcAddress = srcAddress.replace(', ',' ').replace(',',' ').replace(' '.'+') 
	dstAddress = dstAddress.replace(', ',' ').replace(',',' ').replace(' ','+')
	# Compose a URL to query a predefined location with a radius of 5000 m
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + srcAddress + "&destinations=" + dstAddress + "&mode=walking"
	# Send the GET request to the Place details service (using aove url)
	response = urllib2.urlopen(url)
	# Processing the response
	json_raw = response.read()
	json_data = json.loads(json_raw)
	if json_data['status'] == 'OK':
		rows = json_data['rows'][0]
		elements = rows["elements"][0]
		#distance = legs["distance"]
		duration = elements["duration"]
		time = duration["value"]
		return time
	else:
		# Couldnt find the distance - default to a large value
		return 9999

def maxWalkingTime(query=''):
	walk_time = 20
	eating_time = 30
	total_time = eating_time + (2*walk_time)
	if (total_time - 40) < 30:
		max_walk = 15*60
	else:
		max_walk = 20*60
	info = {}
	results = defaultdict(dict)
	cl = db.connect()
	if query == '':
		sql_query = "SELECT FROM Restaurant"
	else:
		sql_query = "SELECT FROM Restaurant WHERE cuisines LIKE " + "\'%" +query.lower() + "%\'" + " OR name LIKE " + "\'%" + query.title() + "%\'" + " OR address LIKE " + "\'%" + query.title() + "%\'" 
	res = cl.command(sql_query)
	print "Query executed " + sql_query
	for item in res:
		if getDuration(item.address) <= max_walk:
			info[item.rid] = getDuration(item.address) #Will be changed to health score later
		else:
			continue
		#print item.name
		results[item.rid]['distance'] = info[item.rid]
                results[item.rid]['address'] = item.address
                results[item.rid]['latitude'] = item.latitude
                results[item.rid]['longitude'] = item.longitude
                results[item.rid]['mobile_url'] = item.mobile_url
                results[item.rid]['rating'] = item.rating
                results[item.rid]['name'] = item.name
                results[item.rid]['res_id'] = item.res_id
                results[item.rid]['review_count'] = item.review_count
                results[item.rid]['cuisines'] = item.cuisines
                #results[item.rid]['health_index'] = "{0:.2f}".format(item.health_index*10)
                results[item.rid]['health_option'] = item.health_option
                results[item.rid]['image_url'] = item.image_url
	rids = sorted(info, key=info.get)[:5]
	result = defaultdict(dict)
	for key in rids:
		result[key] = results[key]
	result = sorted(result.values(), key=lambda x:int(x["health_option"]), reverse=True)
	print result			
	#return result

def searchByLoc(uid, srclat, srclong, query=''):
	srclat = float(srclat)
	srclong = float(srclong)
	info = {}
	results = defaultdict(dict)
	cl = connect()
	if query == '':
		sql_query = "SELECT FROM Restaurant"
	else:
		sql_query = "SELECT FROM Restaurant WHERE cuisines LIKE " + "\'%" +query.lower() + "%\'" + " OR name LIKE " + "\'%" + query.title() + "%\'" + " OR address LIKE " + "\'%" + query.title() + "%\'" 

def search_res(uid,query='',srclat='',srclong=''):
	print "In search API"
	print uid,query,srclat,srclong
	if query == '':
		if srclat == '' and srclong == '':
			print "Query is empty and Location is turned off"
			result = searchByPref(uid)
		else:
			print "Query is empty and Location is turned on"
			result = searchByLoc(uid, srclat, srclong)
	elif srclat == '' and srclong =='' :
		print "Query is not empty but location is turned off"
		result = searchByPref(uid, query)
	else:
		print "Query is not empty and Location is turned on"
		result = searchByLoc(uid, srclat, srclong, query)
	return result

def searchByPref(uid, query=''):
	info = {}
	results = defaultdict(dict)
	cl = connect()
	if query == '':
		sql_query = "SELECT FROM Restaurant"
	else:
		sql_query = "SELECT FROM Restaurant WHERE cuisines LIKE " + "\'%" +query.lower() + "%\'" + " OR name LIKE " + "\'%" + query.title() + "%\'" + " OR address LIKE " + "\'%" + query.title() + "%\'" 
	res = cl.command(sql_query)
	print "Query executed " + sql_query
	for item in res:
		#print dir(item)
		info[item.rid] = item.rating #Will be changed to health score later
                results[item.rid]['address'] = item.address
                results[item.rid]['latitude'] = item.latitude
                results[item.rid]['longitude'] = item.longitude
                results[item.rid]['mobile_url'] = item.mobile_url
                results[item.rid]['rating'] = item.rating
                results[item.rid]['name'] = item.name
                results[item.rid]['res_id'] = item.res_id
                results[item.rid]['review_count'] = item.review_count
                results[item.rid]['cuisines'] = item.cuisines
                #results[item.rid]['health_index'] = "{0:.2f}".format(item.health_index*10)
                results[item.rid]['health_option'] = item.health_option
                results[item.rid]['image_url'] = item.image_url
	rids = sorted(info, key=info.get)[:5]
	result = defaultdict(dict)
	for key in rids:
		result[key] = results[key]
	result = sorted(result.values(), key=lambda x:int(x["health_option"]), reverse=True)
	print result			
	return result

def searchByLoc(uid, srclat, srclong, query=''):
	srclat = float(srclat)
	srclong = float(srclong)
	info = {}
	results = defaultdict(dict)
	cl = connect()
	if query == '':
		sql_query = "SELECT FROM Restaurant"
	else:
		sql_query = "SELECT FROM Restaurant WHERE cuisines LIKE " + "\'%" +query.lower() + "%\'" + " OR name LIKE " + "\'%" + query.title() + "%\'" + " OR address LIKE " + "\'%" + query.title() + "%\'" 
	res = cl.command(sql_query)
	print "Query executed " + sql_query
	for item in res:
		#print dir(item)
		lat = float(item.latitude)
		long = float(item.longitude)
		# Accoding to the requirements can be changed to get distance
		duration = getDistance(srclat,srclong,lat,long)
		#print "I got duration"
		info[item.rid] = duration
		results[item.rid]['distance'] = duration
                results[item.rid]['address'] = item.address
                results[item.rid]['latitude'] = item.latitude
                results[item.rid]['longitude'] = item.longitude
                results[item.rid]['mobile_url'] = item.mobile_url
                results[item.rid]['rating'] = item.rating
                results[item.rid]['name'] = item.name
                results[item.rid]['res_id'] = item.res_id
                results[item.rid]['review_count'] = item.review_count
                results[item.rid]['cuisines'] = item.cuisines
                #results[item.rid]['health_index'] = "{0:.2f}".format(item.health_index*10)
                results[item.rid]['health_option'] = item.health_option
                results[item.rid]['image_url'] = item.image_url
	print "Finished fetching results"
	rids = sorted(info, key=info.get)[:5]
	print str(len(rids))
	result = defaultdict(dict)
	print "Returning Top 5"
	for key in rids:
		result[key] = results[key]
	result = sorted(result.values(), key=lambda x:int(x["health_option"]), reverse=True)
	print result			
	return result
		
if __name__ == "__main__":
	#search_res(uid,slat,slong)
	maxWalkingTime()
