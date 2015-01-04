import topgenerator as tp
import json
import math
from collections import defaultdict
import urllib2

slat = 40.113824
slong = -88.207785
uid = 234
def rad(x):
	return x * math.pi / 180

def getDistance(srclat, srclong, dstlat, dstlong):
	R = 6378137L
	dLat = rad(dstlat - srclat)
	dLong = rad(dstlong - srclong)
	a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(srclat)) * math.cos(rad(dstlat)) * math.sin(dLong / 2) * math.sin(dLong / 2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	d = R * c
	return d

def getDuration(srclat, srclong, dstlat, dstlong):
	# Setting the Google Places API key
	AUTH_KEY = 'AIzaSyACzP9Vt7RxrLFqwsG4SkVGRIiSJC1kEWo'
	# Prepare the sourceLatLong and dstLatLong
	sourceLatLong = str(srclat) + ',' + str(srclong)
	dstLatLong = str(dstlat) + ',' + str(dstlong)
	# Compose a URL to query a predefined location with a radius of 5000 m
	url = "https://maps.googleapis.com/maps/api/directions/json?origin="+sourceLatLong+"&destination="+dstLatLong+"&key="+AUTH_KEY+"&mode=walking&alternatives=true"
	# Send the GET request to the Place details service (using aove url)
	response = urllib2.urlopen(url)
	# Processing the response
	json_raw = response.read()
	json_data = json.loads(json_raw)
	if json_data['status'] == 'OK':
		routes = json_data['routes'][0]
		legs = routes["legs"][0]
		#distance = legs["distance"]
		duration = legs["duration"]
		time = int(duration["text"].split()[0])
		return time
	else:
		# Couldnt find the distance - default to a large value
		return 9999

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
	cl = tp.connect()
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
                results[item.rid]['health_index'] = "{0:.2f}".format(item.health_index*10)
                results[item.rid]['image_url'] = item.image_url
	rids = sorted(info, key=info.get)[:5]
	result = defaultdict(dict)
	for key in rids:
		result[key] = results[key]
	result = sorted(result.values(), key=lambda x:float(x["health_index"]), reverse=True)
	print result			
	return result

def searchByLoc(uid, srclat, srclong, query=''):
	srclat = float(srclat)
	srclong = float(srclong)
	info = {}
	results = defaultdict(dict)
	cl = tp.connect()
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
                results[item.rid]['health_index'] = "{0:.2f}".format(item.health_index*10)
                results[item.rid]['image_url'] = item.image_url
	print "Finished fetching results"
	rids = sorted(info, key=info.get)[:5]
	print str(len(rids))
	result = defaultdict(dict)
	print "Returning Top 5"
	for key in rids:
		result[key] = results[key]
	result = sorted(result.values(), key=lambda x:float(x["health_index"]), reverse=True)
	print result			
	return result
		
if __name__ == "__main__":
	search_res(uid,slat,slong)
