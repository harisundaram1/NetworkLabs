# -*- coding: utf-8 -*-
# Import the relevant libraries
import sys
import urllib
import urllib2
import json
import oauth2
import re

# Setting the Google Places API key
AUTH_KEY = 'AIzaSyACzP9Vt7RxrLFqwsG4SkVGRIiSJC1kEWo'

# Yelp OAuth credential placeholders 
CONSUMER_KEY = 'EsM_GLON6beInS2wRqll3A'
CONSUMER_SECRET = 'VsPvQJp0B7l9Fyq7fO6P1bvd8_4'
TOKEN = '03tV9LL90-vIp0JwdR35N_sQK8VWR_9i'
TOKEN_SECRET = 'LlwCEHA27akrocjGwCvg0HW2ffc'

# Defining a Class for Search
def generate(city):
	print "-----------------------------\n Looking up Restaurants \n-----------------------------\n"
	for i in range(0,18):
		term = 'restaurant'
		limit = 20
		offset = i
		#encoded_params = urllib.urlencode(url_params)

		url = 'http://api.yelp.com/v2/search?term=' + term + '&location=' + city + '&limit=' + str(limit) + '&offset=' + str(offset)

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

		#total = json_data['total']
		outfile = open("Restaurant_Data.txt","a")
		
		for place in json_data['businesses']:
			items = []
			for i in place['categories']:
				for j in i:
					items.append(j)
			categories = '[' + ",".join(item for item in items) + ']'
			outfile.write(place['id'] + ',' + place['name'] + ',' + place['display_phone'] + ',' + place['mobile_url'] + ',' + 
						 categories + ',' + str(place['review_count']) + ',' + str(place['rating']) +  '\n')
		
		outfile.close()
		

#class Search

if __name__ == "__main__":
	# Pass the city
	generate('Champaign')
	