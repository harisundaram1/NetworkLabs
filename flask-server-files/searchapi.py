import topgenerator as tp
import json
import math
from collections import defaultdict

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
		sql_query = "SELECT FROM Restaurant WHERE cuisines LIKE " + "\'%" +query + "%\'" + " OR name LIKE " + "\'%" + query + "%\'" + " OR address LIKE " + "\'%" + query + "%\'" 
	print sql_query
	res = cl.command(sql_query)
	print "Query executed" + query
	for item in res:
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
	rids = sorted(info, key=info.get)[:5]
	result = defaultdict(dict)
	for key in rids:
		result[key] = results[key]
	print result.values()			
	return result.values()			

def searchByLoc(uid, srclat, srclong, query=''):
	srclat = float(srclat)
	srclong = float(srclong)
	info = {}
	results = defaultdict(dict)
	cl = tp.connect()
	if query == '':
		sql_query = "SELECT FROM Restaurant"
	else:
		sql_query = "SELECT FROM Restaurant WHERE cuisines LIKE " + "\'%" +query + "%\'" + " OR name LIKE " + "\'%" + query + "%\'" + " OR address LIKE " + "\'%" + query + "%\'" 
	res = cl.command(sql_query)
	print "Query executed" + sql_query
	for item in res:
		lat = float(item.latitude)
		long = float(item.longitude)
		info[item.rid] = getDistance(srclat,srclong,lat,long)
		results[item.rid]['distance'] = getDistance(srclat,srclong,lat,long)
                results[item.rid]['address'] = item.address
                results[item.rid]['latitude'] = item.latitude
                results[item.rid]['longitude'] = item.longitude
                results[item.rid]['mobile_url'] = item.mobile_url
                results[item.rid]['rating'] = item.rating
                results[item.rid]['name'] = item.name
                results[item.rid]['res_id'] = item.res_id
                results[item.rid]['review_count'] = item.review_count
                results[item.rid]['cuisines'] = item.cuisines
	print "Finished fetching results"
	rids = sorted(info, key=info.get)[:5]
	result = defaultdict(dict)
	print "Returning Top 5"
	for key in rids:
		result[key] = results[key]
	print result.values()			
	return result.values()	
		
if __name__ == "__main__":
	search_res(uid,slat,slong)
