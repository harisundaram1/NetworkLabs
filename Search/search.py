# -*- coding: utf-8 -*-
# Import the relevant libraries
import sys
import urllib
import urllib2
import json
import oauth2

# Setting the Google Places API key
AUTH_KEY = 'AIzaSyACzP9Vt7RxrLFqwsG4SkVGRIiSJC1kEWo'

# Yelp OAuth credential placeholders 
CONSUMER_KEY = 'EsM_GLON6beInS2wRqll3A'
CONSUMER_SECRET = 'VsPvQJp0B7l9Fyq7fO6P1bvd8_4'
TOKEN = '03tV9LL90-vIp0JwdR35N_sQK8VWR_9i'
TOKEN_SECRET = 'LlwCEHA27akrocjGwCvg0HW2ffc'

def requestYelp(latlong):
	print "-----------------------------\n Using Yelp API"
	term = 'restaurant'
	limit = 5    
	#encoded_params = urllib.urlencode(url_params)

	url = 'http://api.yelp.com/v2/search?term=' + term + '&ll=' + latlong + '&limit=' + str(limit)

	#'http://{0}{1}?{2}'.format(host, path, encoded_params)

	consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
	oauth_request = oauth2.Request('GET', url, {})
	oauth_request.update(
		{
			'oauth_nonce': oauth2.generate_nonce(),
			'oauth_timestamp': oauth2.generate_timestamp(),
			'oauth_token': TOKEN,
			'oauth_consumer_key': CONSUMER_KEY
		}
	)
	token = oauth2.Token(TOKEN, TOKEN_SECRET)
	oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_request.to_url()

	conn = urllib2.urlopen(signed_url, None)
	try:
		json_data = json.loads(conn.read())
	finally:
		conn.close()

	#if json_data['status'] == 'OK':
	for place in json_data['businesses']:
		print '%s\n' % (place['name'])

def requestGoogle(latlong,radius=5000):
	print "Using Google Places"
	types='restaurant'
	# Compose a URL to query a predefined location with a radius of 5000 meters
	url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s'
         '&radius=%s&types=%s&key=%s') % (latlong, radius, types, AUTH_KEY)

	# Send the GET request to the Place details service (using url from above)
	response = urllib2.urlopen(url)
	
	# Get the response and use the JSON library to decode the JSON
	json_raw = response.read()
	json_data = json.loads(json_raw)

	# Iterate through the results and print them to the console
	if json_data['status'] == 'OK':
	  for place in json_data['results']:
		if 'food' in set(place['types']):
			print (place['name']).encode('utf-8')
	
#-------------------------------------------
# The main routine
#-------------------------------------------
if __name__ == "__main__":
	
	if len(sys.argv) < 3:
		# Default Location
		latlong = '40.113803,-88.224905'
	else:
		latlong = sys.argv[1]+","+sys.argv[2]
	print latlong
	requestGoogle(latlong)
	requestYelp(latlong)
