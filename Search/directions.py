# -*- coding: utf-8 -*-

# Generic framework for both routes and restaurant
# restaurant - look at the menu
# health index - salads, fish & chicken - higher score (roasted bu not stew, find out)
				#dessert, pork , beef - lower score
#table should have avg cost, veg friendly,


# Import the relevant libraries
import sys
import urllib
import urllib2
import json
import oauth2
import re

# Setting the Google Places API key
AUTH_KEY = 'AIzaSyACzP9Vt7RxrLFqwsG4SkVGRIiSJC1kEWo'

def requestGoogle(srclatlong,dstlatlong):
	print "Using Google Places"
	types='restaurant'
	# Compose a URL to query a predefined location with a radius of 5000 meters
	url = ('https://maps.googleapis.com/maps/api/directions/json?origin=%s'
         '&destination=%s&key=%s&mode=walking&alternatives=true') % (srclatlong, dstlatlong, AUTH_KEY)

	# Send the GET request to the Place details service (using url from above)
	response = urllib2.urlopen(url)
	
	# Get the response and use the JSON library to decode the JSON
	json_raw = response.read()
	json_data = json.loads(json_raw)
	#print json_data['routes']['legs']
	# Iterate through the results and print them to the console
	if json_data['status'] == 'OK':
		items = json_data['routes']
		for item in items:
			print "\n" + "Route" "\n"
			legs = item['legs']
			for step in legs:
				steps = step['steps']
				for step in steps:
					print re.sub('<[^<]+?>', '', step['html_instructions']) + " - " +step['distance']['text']
			#for steps in route['steps']:
			#	print steps['html_instructions'] + steps['duration']['text'] + "\n"
	
#-------------------------------------------
# The main routine
#-------------------------------------------
if __name__ == "__main__":
	
	if len(sys.argv) < 3:
		# Default Location
		srclatlong = '40.113803,-88.224905'
		dstlatlong = '40.109789,-88.227261'
	else:
		srclatlong = sys.argv[1]+","+sys.argv[2]
		dstlatlong = sys.argv[3]+","+sys.argv[4]
	print srclatlong, dstlatlong
	requestGoogle(srclatlong,dstlatlong)
	
