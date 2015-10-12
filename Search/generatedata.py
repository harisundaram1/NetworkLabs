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


# -*- coding: utf-8 -*-
# Import the relevant libraries
import sys
import urllib
import urllib2
import json
import oauth2
import re
import io

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
	outfile = io.open('Restaurant_Data.txt','w',encoding='utf8')
	for i in range(0,18):
		term = 'restaurant'
		limit = 20
		if i==0:
			url = 'http://api.yelp.com/v2/search?term=' + term + '&location=' + city + '&limit=' + str(limit)
		else:
			url = 'http://api.yelp.com/v2/search?term=' + term + '&location=' + city + '&limit=' + str(limit) + '&offset=' + str(limit*i)
		#encoded_params = urllib.urlencode(url_params)

		#url = 'http://api.yelp.com/v2/search?term=' + term + '&location=' + city + '&limit=' + str(limit) + '&offset=' + str(offset)

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
		
		
		for place in json_data['businesses']:
			items = []
			for i in place['categories']:
				for j in i:
					items.append(j)
			categories = '[' + ",".join(item for item in items) + ']'
			outfile.write(place['id'] + ',' + place['name'] + ',' + place['mobile_url'] + ',' + 
						 categories + ',' + str(place['review_count']) + ',' + str(place['rating']) +  '\n')
		
	outfile.close()
		

#class Search

if __name__ == "__main__":
	# Pass the city
	generate('Champaign')
	
