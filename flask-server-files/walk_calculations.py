import json
import math
from collections import defaultdict
import urllib2
import pyorient
import searchapi
import datetime

STEPS_PER_MINUTE = 133

def steps_walked(card_id):
	# Connect to DB and fetch Card
	# Get the last is_going card by the same user today
	# Get the lat long from is_going_card and restaurant lat_long from the post
	# find the distance between them hence the steps walked
	print "in steps_walked"
	print card_id
	cl = searchapi.connect()
	# Get card
	sql_query = "select from #"+card_id
	post_card = cl.command(sql_query)[0]
	today = datetime.date.today().strftime('%s')+"000"

	#Get is_going card
	sql_query = 'select from card where display_type="is_going" and first_name="'+post_card.first_name+'" and last_name="'+post_card.last_name+'" and created_at>='+today+' and location_name="'+post_card.location_name+'" order by created_at desc'
	print sql_query
	result = cl.command(sql_query)
	print result
	if result == []:
		#I AM GOING card not found
		print 'GOING not found'
		steps_walked = 0
	else:
		print "rest found"
		is_going_card = result[0]

		src_lat = is_going_card.user_latitude
		src_long = is_going_card.user_longitude

		# Find Restaurant 
		sql_query = 'select from Restaurant where name="'+post_card.location_name.replace('[','').replace(']','')+'"'
		restaurant = cl.command(sql_query)[0]

		dest_lat = restaurant.latitude
		dest_long = restaurant.longitude	

		# Find distance
		print(src_lat, src_long, dest_lat, dest_long)
		distane = searchapi.get_distance(src_lat, src_long, dest_lat, dest_long)
		duration = searchapi.get_duration(src_lat, src_long, dest_lat, dest_long)
		print 'duration:'+str(duration)
		steps_walked = int(duration/60) * STEPS_PER_MINUTE

		# Update the post_card
		cl.command('Update Card set steps_walked='+str(steps_walked)+' where @rid=#'+card_id)
	return steps_walked
