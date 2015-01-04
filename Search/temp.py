
import sys
import urllib
import urllib2
import json
import oauth2
import re
import io
import topgenerator as tp

# Yelp OAuth credential placeholders 
CONSUMER_KEY = 'EsM_GLON6beInS2wRqll3A'
CONSUMER_SECRET = 'VsPvQJp0B7l9Fyq7fO6P1bvd8_4'
TOKEN = '03tV9LL90-vIp0JwdR35N_sQK8VWR_9i'
TOKEN_SECRET = 'LlwCEHA27akrocjGwCvg0HW2ffc'

data =[]
city = 'Champaign'

for i in range(0,18):
	term = 'restaurant'
	limit = 20
	if i==0:
	        url = 'http://api.yelp.com/v2/search?term=' + term + '&location=' + city + '&limit=' + str(limit)
     	else:
        	url = 'http://api.yelp.com/v2/search?term=' + term + '&location=' + city + '&limit=' + str(limit) + '&offset=' + str(limit*i)
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
	for place in json_data['businesses']:
		try:
			place["image_url"]
			image = place["image_url"]
        		data.append((image, place['id']))
		except:
			image = ""
        		data.append((image, place['id']))

cl = tp.connect()
count = 0
for items in data:
	if items[0] == "":
		continue
	else:
		query = "UPDATE Restaurant SET image_url='"+items[0].encode('ascii', 'ignore') + "' where res_id='" + items[1].encode('ascii', 'ignore')+"'"
		cl.command(query)
		count += 1
print str(count)
