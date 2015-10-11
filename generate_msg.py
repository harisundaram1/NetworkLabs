Copyright (c) 2015 Crowd Dynamics Labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

from script import find_images,is_int,ignore,relevance_score,find_weight,begin_localimg

import pyorient
import json
import collections
import operator
import time
#from collections import Counter
from pyorient.utils import *
import datetime
import random
import matplotlib.pyplot as plt
import base64

positive_messages = []
negative_messages = []
most_influential_num_pos = (0,0,0)
most_influential_msg_pos = ""
most_influential_num_neg = (0,0,0)
most_influential_msg_neg = ""
delta = datetime.timedelta(days=1)

def connect():
	#print "in connect"
	client = pyorient.OrientDB("localhost", 2424)
	session_id = client.connect( "root", "rootlabs" )
	client.db_open( "NetworkLabs", "root", "rootlabs")
	return client

def get_friends(rid):
	cl = connect()
#	print "Retrieving rid's of friends"
	friends = cl.command("select expand(both('friends_with')) from Person where @rid = "+str(rid))
	return friends

def create_binary_data(path):
#        print 'saving the graphs as nodes'
        cl = connect()
        file_names = []
	file_names.append(path)
        # print file_names
        for fl in file_names:
                print 'creating node for image '+fl
                with open(fl,mode='rd') as img_file:
                        encoded_str = base64.b64encode(img_file.read())
               	res =cl.command('create vertex BinaryData set data="'+encoded_str+'"')
		return res[0].rid


def plotbarchart(x,y,xlabels,xaxis,yaxis,graph_title,bar_color):
	print "In plot bar chart"
	fig = plt.figure()
	#plt.bar(x,y,align='center',color=bar_color)
	plt.bar(x,y,color=bar_color)
#	plt.tight_layout()
	plt.xticks(x,xlabels)
	fig.autofmt_xdate()
	fig.suptitle(graph_title, fontsize=15)
	plt.xlabel(xaxis)
	plt.ylabel(yaxis)
	fig.savefig("barchart.jpg")
	recid_img = create_binary_data("/home/chndrsh4/barchart.jpg")
#	plt.tight_layout()
	return recid_img

def check_health_index(rname):
	cl = connect()
	cmd_health_options = "select health_option from Restaurant where name =\""+str(rname)+"\""
#	print cmd_health_options
	rest_details = cl.command(cmd_health_options)

	#print rest_details
	#print rest_details[0].health_option
	if (rest_details[0].health_option>30):
		return 1
	else:
		return 0

def check_health_index_id(rid):
	cl = connect()
	cmd_health_options = "select health_option from Restaurant where res_id =\""+str(rid)+"\""
#	print cmd_health_options
	rest_details = cl.command(cmd_health_options)

	#print rest_details
	#print rest_details[0].health_option
	if (rest_details[0].health_option>30):
		return 1
	else:
		return 0

def find_healthy_visits(visit_counts):
    healthy_eats = 0
    unhealthy_eats = 0
    for key,val in visit_counts.items():
#		print key
#		print val
		if (check_health_index_id(key)):
			healthy_eats = healthy_eats+val
		else:
			unhealthy_eats = unhealthy_eats+val	
    return(healthy_eats,unhealthy_eats)

def count_visits(visited_rest):
	visited_count = {}
	for rest in visited_rest:
		if rest.res_id in visited_count:
			visited_count[rest.res_id] = visited_count[rest.res_id]+1
		else:
			visited_count[rest.res_id] = 1
	asorted_restaurant_visits = sorted(visited_count.items(), key=operator.itemgetter(1))
	dsorted_restaurant_visits = sorted(visited_count.items(), key=operator.itemgetter(1), reverse=True)
	return (visited_count,asorted_restaurant_visits,dsorted_restaurant_visits)


def insert_card(cmd_str,recordid,card_type=0):
    card_record = cl.command(cmd_str)
#    print card_record
    rec_id = card_record[0].rid
    print rec_id
    cl.command('create edge can_view from '+str(recordid)+' to '+str(rec_id))
    print "Successfully inserted"
    if card_type ==1: # Indicates an image has to be inserted
	return rec_id

def count_cuisines_eaten(all_restaurants_eaten):
    cuisine_count = {}
    asc_cuisine = []
    desc_cuisine = []
    all_cuisines = []
    cl = connect()
    flag = 0
    for restaurants in all_restaurants_eaten:
        if len(restaurants)>=1:
	    flag = 1
            for rest in restaurants:
                if(check_health_index_id(rest.res_id)):
#		    print rest
                    #Find the type of cuisine eaten
		    cmd_str = "select cuisines as cuisine from Restaurant where res_id=\""+str(rest.res_id)+"\""
		   # print cmd_str
                    rest_cuisine = cl.command(cmd_str) 
		   # for cuisine in rest_cuisine:
#			print cuisine
                    all_cuisines = rest_cuisine[0].cuisine[0].split(",")[1::2]
                    for i in all_cuisines:
                        if i in cuisine_count.keys():
                            cuisine_count[i] += 1
                        else:
                            cuisine_count[i] = 1
                    asc_cuisine = sorted(cuisine_count.items(), key=operator.itemgetter(1))
                    desc_cuisine = sorted(cuisine_count.items(), key=operator.itemgetter(1), reverse=True)
    if flag==1:
	    return (cuisine_count,asc_cuisine,desc_cuisine)
    else:
	    return ("","","")

def count_restaurants_visited(all_restaurants_eaten):
	restaurant_visits = {}
	asorted_restaurant_visits = []
	dsorted_restaurant_visits = []
	flag = 0
	for restaurants in all_restaurants_eaten:
		if len(restaurants)>=1:
			flag =1
			for rest in restaurants:
#				print rest
#		print rest.name
				if(check_health_index_id(rest.res_id)):
					if rest.res_id in restaurant_visits:
						restaurant_visits[rest.res_id] += 1
					else:
						restaurant_visits[rest.res_id] = 1
			asorted_restaurant_visits = sorted(restaurant_visits.items(), key=operator.itemgetter(1))
			dsorted_restaurant_visits = sorted(restaurant_visits.items(), key=operator.itemgetter(1), reverse=True)
	if flag==1:
		return (restaurant_visits,asorted_restaurant_visits,dsorted_restaurant_visits)
	else:
		return ("","","")

def count_healthy_users(all_healthy_eaten):
    visit_counts_user = {}
    desc_visitcount = []
    asc_visitcount = []    
    (healthy_users,unhealthy_users) = (0,0)
    (healthy_visits,unhealthy_visits) = (0,0)
    for visit in all_healthy_eaten:
        if len(visit)>=1:
            (visit_counts_user,desc_visitcount,asc_visitcount) = count_visits(visit)
            (healthy_visits,unhealthy_visits) = find_healthy_visits(visit_counts_user)
	    if healthy_visits>=unhealthy_visits:
		healthy_users+=1
	    else:
		unhealthy_users+=1
    return (healthy_users,unhealthy_users)

def get_restaurant_name(rid,code=0):
	cl = connect()
	cmd_str = "select name,@rid as rid from Restaurant where res_id='"+str(rid)+"'"
#	print cmd_str
	rest = cl.command(cmd_str)
#	print rest
	if code==1:
		return (str(rest[0].name),rest.rid)
	else:
		return str(rest[0].name)


def compute_spatial_stats(all_restaurants_eaten):
	rest_spatial_stats = {'North Urbana':0,'South Urbana':0,'North Champaign':0,'South Champaign':0}
	flag = 0
	max_index = 0
	area_list = []
	for restaurants in all_restaurants_eaten:
		if len(restaurants)>=1:
			flag = 1
			area_list = [0,0,0,0] #index0: north urbana;index1:south urbana;index2: north champaign;index3:south champaign
			for rest in restaurants:
				cmd_str = "select latitude as lat, longitude as lon from Restaurant where res_id='"+str(rest.res_id)+"'"
		#		print cmd_str
				rest_coord = cl.command(cmd_str)
				if (rest_coord[0].lat > 40.11150 and rest_coord[0].lon>-88.22900 ):
					area_list[0]+=1
				elif (rest_coord[0].lat < 40.11150 and rest_coord[0].lon>-88.22900):
					area_list[1] +=1
				elif (rest_coord[0].lat > 40.11150 and rest_coord[0].lon<-88.22900  ):
					area_list[2] +=1
				#(rest.lat < 40.11150 and rest.lon<-88.22900  ):
				else:
					area_list[3] +=1
		#max_index = area_list.index(max(area_list))
			if area_list[0]>0:
				rest_spatial_stats["North Urbana"] +=1
			if area_list[1]>0:
				rest_spatial_stats["South Urbana"] +=1
			if area_list[2]>0:
				rest_spatial_stats["North Champaign"] +=1
			if area_list[3]>0:
				rest_spatial_stats["South Champaign"] +=1
			asorted_rest_spatial_stats = sorted(rest_spatial_stats.items(), key=operator.itemgetter(1))
			dsorted_rest_spatial_stats = sorted(rest_spatial_stats.items(), key=operator.itemgetter(1), reverse=True)
	if flag ==1:
		return (rest_spatial_stats,asorted_rest_spatial_stats,dsorted_rest_spatial_stats)
	else:
		return ("","","")


def calc_stats(total_friends,dsorted_rest_visits):
	if len(dsorted_rest_visits)>=1:
		visited = dsorted_rest_visits[0][1]
		notvisited = total_friends-visited
		percent_visited = (float(visited)/total_friends)*100
		percent_notvisited = (float(notvisited)/total_friends)*100
#	print dsorted_rest_visits
		restaurant_name = get_restaurant_name(dsorted_rest_visits[0][0])
		return(visited,notvisited,percent_visited,percent_notvisited,restaurant_name)
	else:
		return ("","","","","")

def find_epoch_time():
	current_epoch_time = int(time.time())
	week_ago = current_epoch_time*1000 - 604800000
	month_ago = current_epoch_time*1000 - 2629743000
#	print "Epoch week is "+ str(week_ago)
#	print "Epoch month is "+ str(month_ago)
	return (week_ago,month_ago)

def walking_message(steps,msg_start,total_users):
#	print "In walking messages"
#	print steps
#	print msg_start
	mesg = ""
	if steps in range(0,100000):
	#	print "In if 1"
		more_steps = 100000- steps
		avg_steps = more_steps/total_users
		mesg = ''+str(msg_start)+" "+str(avg_steps)+" more steps each, you'll would have collectively walked a total of 100000 steps"
	elif steps in range(100000,300000):
	#	print "in if 2"
		more_steps =  280896-steps
		avg_steps = more_steps/total_users
		print more_steps
		mesg = ''+str(msg_start)+' '+str(avg_steps)+" more steps each, you'll would have collectively walked all the way from Champiagn-Urbana to Chicago "
		mesg = str(mesg)
		print mesg
	#	print "End of if"
	elif steps in range(300000,16739712):
		more_steps = 16739712-steps
		avg_steps = more_steps/total_users
		mesg = ''+str(msg_start)+" "+str(avg_steps)+" more steps each, you'll would have collectively walked a full circle around the earth"
	elif steps in range(16739712,504556800):
		more_steps = 504556800-steps
		avg_steps = more_steps/total_users
		mesg = ''+str(msg_start)+" "+str(avg_steps)+" more steps each, you'll would have collectively walked from the earth to the moon"
	else:
		print "Matches no if's"
		mesg = "Houston we have a problem"
#	print "Matches no other if's"
	return str(mesg)

def check_data_existence(all_stats):
	count =0
	for res in all_stats:
		if not res:
			count +=1
	if count==len(all_stats):
		return 0
	else:
		return 1
	

def categorize_messages(num,den,msg_tail,template_type):
	global positive_messages
	global negative_messages
	global most_influential_num_pos
	global most_influential_num_neg
	global most_influential_msg_pos
	global most_influential_msg_neg
	percent = num/den*100
	print num
	print msg_tail
	msg_type_stat = 0
	if percent >60:
		msg_type_stat = 1
		if den>10 and percent>num:
			msg_type = 0 #msg_type =0 indicates use of percentage
			msg = ''+str(percent)+' % of'+str(msg_tail)
		else:
			msg_type = 1 #use the "out of" notation
			msg = ''+str(num)+' out of '+str(den)+' '+str(msg_tail)
	elif percent in range(45,60):
		msg_type_stat = 0
		if den>10:
			msg_type = 0 #msg_type =0 indicates use of percentage
			msg = ''+str(percent)+' % of'+str(msg_tail)
		else:
			msg_type = 1 #use the "out of" notation
			msg = ''+str(num)+' out of '+str(den)+' '+str(msg_tail)
	else:
		msg_type_stat = -1
		if den>10 and percent<num:
			msg_type = 0 #msg_type =0 indicates use of percentage
			msg = ''+str(percent)+' % of'+str(msg_tail)
		else:
			msg_type = 1 #use the "out of" notation
			msg = ''+str(num)+' out of '+str(den)+' '+str(msg_tail)
	if template_type==1 and msg_type_stat==1:
		positive_messages.append(msg)
		print most_influential_num_pos[0]
		print percent
		print most_influential_num_pos[1]
		print num
		if percent>most_influential_num_pos[0] or num>most_influential_num_pos[1]:
			most_influential_num_pos = (percent,num,den)
			most_influential_msg_pos = msg 
	elif template_type==-1 and msg_type_stat==-1:
		print most_influential_num_pos[0]
                print percent
                print most_influential_num_pos[1]
                print num
		positive_messages.append(msg)
		if percent>most_influential_num_pos[0] or num>most_influential_num_pos[1]:
			most_influential_num_pos = (percent,num,den)
			most_influential_msg_pos = msg 
	elif template_type==-1 and msg_type_stat==1:
		negative_messages.append(msg)
		if percent<most_influential_num_pos[0] or num<most_influential_num_pos[1]:
			most_influential_num_neg = (percent,num,den)
			most_influential_msg_neg = msg 
	else:
		negative_messages.append(msg)
		if percent<most_influential_num_pos[0] or num<most_influential_num_pos[1]:
			most_influential_num_neg = (percent,num,den)
			most_influential_msg_neg = msg 
	print msg
	print most_influential_msg_pos
	print most_influential_msg_neg	
			

def rest_visited_by_friends(rid,msg_type,restaurant_name=""):
	cl = connect()        
	steps_walked = 0
	all_friends_rest_visits = []
	all_friends_healthy_visits = []
	all_friends_healthy_visits_weekly = []
	all_friends_healthy_visits_monthly = []
	all_friends_rest_visits_weekly = []
	all_friends_rest_visits_monthly = []
	all_friends_visits_spatial = []
	all_friends_visits_spatial_weekly = []
	all_friends_visits_spatial_monthly = []
	(epoch_week,epoch_month) = find_epoch_time()

	res1= get_friends(rid)
	total_friends = len(res1)

	for i in range(total_friends):
		friendid = str(res1[i].rid)
		steps_walked += res1[i].steps_walked
		print friendid
		rest_visit = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(both('eats_at')) from Person where @rid = "+friendid+")")
		healthy_visits = cl.command("select name, res_id as res_id from (select expand(both('eats_at')) from Person where @rid = "+friendid+")")
		healthy_visits_weekly = cl.command("select name, res_id as res_id from (select expand(in) from eats_at where created_at > "+str(epoch_week)+" and out="+friendid+")")
		healthy_visits_monthly = cl.command("select name, res_id as res_id from (select expand(in) from eats_at where created_at > "+str(epoch_month)+" and out="+friendid+")")

		rest_visit_weekly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_week)+" and out="+friendid+")")
		rest_visit_monthly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_month)+" and out="+friendid+")")

		all_friends_rest_visits.append(rest_visit)
		all_friends_healthy_visits.append(healthy_visits)
		all_friends_rest_visits_weekly.append(rest_visit_weekly)
		
		all_friends_rest_visits_monthly.append(rest_visit_monthly)
		all_friends_healthy_visits_weekly.append(healthy_visits_weekly)
		all_friends_healthy_visits_monthly.append(healthy_visits_monthly)

		all_friends_visits_spatial.append(rest_visit)
		all_friends_visits_spatial_weekly.append(rest_visit_weekly)
		all_friends_visits_spatial_monthly.append(rest_visit_monthly)

	if (check_data_existence(all_friends_rest_visits)):
		print "Counting visits over all time"
		(restaurant_visits,asorted_restaurant_visits,dsorted_restaurant_visits) = count_restaurants_visited(all_friends_rest_visits)
		print "Computing spatial stats"
		(visits_spatial,asorted_visits_spatial,dsorted_visits_spatial) = compute_spatial_stats(all_friends_visits_spatial)
		print "Counting healthy visits"
		(healthy_friends,unhealthy_friends) = count_healthy_users(all_friends_healthy_visits)
		print "Counting cuisines eaten over all time"
		(cuisines_count,asc_cuisine,desc_cuisine) = count_cuisines_eaten(all_friends_rest_visits)
		
		(visited_alltime,notvisited_alltime,percent_visited_alltime,percent_notvisited_alltime,rname_alltime) = calc_stats(total_friends,dsorted_restaurant_visits)
		(index,w1,w2) = select_random_cuisine(desc_cuisine)
		if dsorted_visits_spatial:
			spatial_index = random.randrange(0,4)
		if(msg_type==1):
			msg = 'Your friends have walked a total of '+str(steps_walked)+' steps'
			print msg
			msg = walking_message(steps_walked,"If you and your friends on an average walk",total_friends)
			print msg
			msg_end = 'of your friends have eaten at '+str(rname_alltime)
			categorize_messages(visited_alltime,total_friends,msg_end,1)
			#msg = ''+str(int(percent_visited_alltime))+' % of your friends have eaten at '+str(rname_alltime)
			#print msg
			#msg = ''+str(visited_alltime)+' out of '+str(total_friends)+' of your friends have eaten at '+str(rname_alltime)
			#print msg
			if spatial_index:
				msg_end = ' of your friends have eaten in '+str(dsorted_visits_spatial[spatial_index][0])
				categorize_messages(dsorted_visits_spatial[spatial_index][1],total_friends,msg_end,1)
#				msg = ''+str(dsorted_visits_spatial[spatial_index][1])+' out of '+str(total_friends)+' of your friends have eaten in '+str(dsorted_visits_spatial[spatial_index][0])
#				print msg

			msg_end = ' of your friends have eaten healthy'
			categorize_messages(healthy_friends,total_friends,msg_end,1)
#				msg = ''+str(healthy_friends)+' out of '+str(total_friends)+' of your friends have eaten healthy'
#				print msg
			if index:
				msg_end = ' of your friends have eaten healthy '+str(desc_cuisine[index][0])
				categorize_messages(desc_cuisine[index][1],total_friends,msg_end,1)
				msg = ''+str(desc_cuisine[index][1])+' out of '+str(total_friends)+' of your friends have eaten healthy '+str(desc_cuisine[index][0])
				print msg
				tags = ["healthy","chinese"]
				ret_val = begin_localimg(msg.replace("1 times","once"),"namedfriend_overlay_cuisine_monthly.jpg")
				if ret_val == 1:
					recid_img = create_binary_data("/Local/Users/dev/NetworkLabs/namedfriend_overlay_cuisine_monthly.jpg")
					cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=1))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",image="'+recid_img+'"'
					card_rid = insert_card(cmd_str,rid,1)
					id_rec = cl.command('create edge has_uploaded_image from '+str(card_rid)+' to '+str(recid_img))
					print id_rec[0].rid
		else:
			msg_end = ' of your friends have not eaten at '+str(rname_alltime)
			categorize_messages(notvisited_alltime,total_friends,msg_end,-1)
#			msg = ''+str(int(percent_notvisited_alltime))+' % of your friends have not eaten at '+str(rname_alltime)
#			print msg
			msg =  ''+str(notvisited_alltime)+' out of '+str(total_friends)+' of your friends have not eaten at '+str(rname_alltime)
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=5))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
#			print cmd_str
			insert_card(cmd_str,rid)
#			print msg
			if spatial_index:
				msg_end = ' of your friends have not eaten in '+str(dsorted_visits_spatial[spatial_index][0])
				categorize_messages(total_friends-dsorted_visits_spatial[spatial_index][1],total_friends,msg_end,-1)
#				msg = ''+str(total_friends-dsorted_visits_spatial[spatial_index][1])+' out of '+str(total_friends)+' of your friends have not eaten in '+str(dsorted_visits_spatial[spatial_index][0])
#				print msg

			msg_end = ' of your friends have not eaten healthy'
			categorize_messages(unhealthy_friends,total_friends,msg_end,-1)
#				msg = ''+str(unhealthy_friends)+' out of '+str(total_friends)+' of your friends have not eaten healthy'
#				print msg
			if index:
				msg_end = ' of your friends have not eaten'+str(w1)+'healthy '+str(desc_cuisine[index][0])+str(w2)
				categorize_messages(total_friends-desc_cuisine[index][1],total_friends,msg_end,-1)
#				msg = ''+str(total_friends-desc_cuisine[index][1])+' out of '+str(total_friends)+' of your friends have not eaten'+str(w1)+'healthy '+str(desc_cuisine[index][0])+str(w2)
#				print msg

	if (check_data_existence(all_friends_rest_visits_weekly)):
		print "Counting weekly visits"
		(weekly_restaurant_visits,asorted_weekly_restaurant_visits,dsorted_weekly_restaurant_visits) = count_restaurants_visited(all_friends_rest_visits_weekly)
		print "Computing spatial stats weekly"
		(visits_spatial_weekly,asorted_visits_spatial_weekly,dsorted_visits_spatial_weekly) = compute_spatial_stats(all_friends_visits_spatial_weekly)
		print "Counting healthy visits weekly"
		(healthy_friends_weekly,unhealthy_friends_weekly) = count_healthy_users(all_friends_healthy_visits_weekly)
		print "Cuisines eaten weekly"
		(cuisines_count_weekly,asc_cuisine_weekly,desc_cuisine_weekly) = count_cuisines_eaten(all_friends_rest_visits_weekly)

		(visited_weekly,notvisited_weekly,percent_visited_weekly,percent_notvisited_weekly,rname_weekly) = calc_stats(total_friends,dsorted_weekly_restaurant_visits)
		if desc_cuisine_weekly:
			(index_weekly,w1_w,w2_w) = select_random_cuisine(desc_cuisine_weekly)
		if dsorted_visits_spatial_weekly:
			spatial_index_weekly = random.randrange(0,4)
		if (msg_type==1):
			msg_end = 'of your friends have eaten at '+str(rname_weekly)+' over the past week'
			categorize_messages(visited_weekly,total_friends,msg_end,1)
#			msg = ''+str(int(percent_visited_weekly))+' % of your friends have eaten at '+str(rname_weekly)+' over the past week'
#			print msg
#			msg = ''+str(visited_weekly)+' out of '+str(total_friends)+' of your friends have eaten at '+str(rname_weekly)+' over the past week'
#			print msg
			msg_end = ' of your friends have eaten healthy over the past week'
			categorize_messages(healthy_friends_weekly,total_friends,msg_end,1)
			msg = '<b>'+str(healthy_friends_weekly)+'</b> out of <b>'+str(total_friends)+'</b> of your friends have eaten healthy <b>over the past week</b>'
			cmd_str = 'create vertex Card set comment_count=0,display_type="info",comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=6))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",content_html="'+msg+'"'
			print cmd_str
			insert_card(cmd_str,rid)
			print msg
			if spatial_index_weekly:
				msg_end = ' of your friends have eaten in '+str(dsorted_visits_spatial_weekly[spatial_index_weekly][0])+' over the past week'
				categorize_messages(dsorted_visits_spatial_weekly[spatial_index_weekly][1],total_friends,msg_end,1)
#				msg = '<b>'+str(dsorted_visits_spatial_weekly[spatial_index_weekly][1])+'</b> out of <b>'+str(total_friends)+'</b> of your friends have eaten in '+str(dsorted_visits_spatial_weekly[spatial_index_weekly][0])+' over the past week'
#				print msg
			if index_weekly:
				msg_end = ' of your friends have eaten'+str(w1_w)+' healthy '+str(desc_cuisine_weekly[index_weekly][0])+str(w2_w)+' over the past week'
				categorize_messages(desc_cuisine_weekly[index_weekly][1],total_friends,msg_end,1)
#				msg = ''+str(desc_cuisine_weekly[index_weekly][1])+' out of '+str(total_friends)+' of your friends have eaten'+str(w1_w)+' healthy '+str(desc_cuisine_weekly[index_weekly][0])+str(w2_w)+' over the past week'
#				print msg
		else:
			msg_end = 'of your friends have not eaten at '+str(rname_weekly)+' over the past week'
			categorize_messages(notvisited_weekly,total_friends,msg_end,-1)
#			msg = ''+str(int(percent_notvisited_weekly))+' % of your friends have not eaten at '+str(rname_weekly)+' over the past week'
#			print msg
#			msg = ''+str(notvisited_weekly)+' out of '+str(total_friends)+' of your friends have not eaten at '+str(rname_weekly)+' over the past week'
#			print msg
			if spatial_index_weekly:
				msg_end = ' of your friends have not eaten in '+str(dsorted_visits_spatial_weekly[spatial_index_weekly][0])+' over the past week'
				categorize_messages(total_friends-dsorted_visits_spatial_weekly[spatial_index_weekly][1],total_friends,msg_end,-1)
#				msg = ''+str(total_friends-dsorted_visits_spatial_weekly[spatial_index_weekly][1])+' out of '+str(total_friends)+' of your friends have not eaten in '+str(dsorted_visits_spatial_weekly[spatial_index_weekly][0])+' over the past week'
#				print msg
			msg_end = ' of your friends have not eaten healthy over the past week'
			categorize_messages(unhealthy_friends_weekly,total_friends,msg_end,-1)
#			msg = ''+str(unhealthy_friends_weekly)+' out of '+str(total_friends)+' of your friends have not eaten healthy over the past week'
#			print msg


	
	if (check_data_existence(all_friends_rest_visits_monthly)):
		print "Counting monthly visits"
		(monthly_restaurant_visits,asorted_monthly_restaurant_visits,dsorted_monthly_restaurant_visits) = count_restaurants_visited(all_friends_rest_visits_monthly)
		print "Computing spatial stats monthly"
		(visits_spatial_monthly,asorted_visits_spatial_monthly,dsorted_visits_spatial_monthly) = compute_spatial_stats(all_friends_visits_spatial_monthly)
		print "Counting healthy visits monthly"
		(healthy_friends_monthly,unhealthy_friends_monthly) = count_healthy_users(all_friends_healthy_visits_monthly)
		print "Cuisines eaten monthly"
		(cuisines_count_monthly,asc_cuisine_monthly,desc_cuisine_monthly) = count_cuisines_eaten(all_friends_rest_visits_monthly)
		
		(visited_monthly,notvisited_monthly,percent_visited_monthly,percent_notvisited_monthly,rname_monthly) = calc_stats(total_friends,dsorted_monthly_restaurant_visits)		
		if desc_cuisine_monthly:
			(index_monthly,w1_m,w2_m) = select_random_cuisine(desc_cuisine_monthly)
		if dsorted_visits_spatial_monthly:
			spatial_index_monthly = random.randrange(0,4)
		if msg_type==1:
			msg_end = 'of your friends have eaten at '+str(rname_monthly)+' over the past month'
			categorize_messages(visited_monthly,total_friends,msg_end,1)
		
#			msg = ''+str(int(percent_visited_monthly))+' % of your friends have eaten at '+str(rname_monthly)+' over the past month'
#			print msg		
	#		msg = ''+str(visited_monthly)+' out of '+str(total_friends)+' of your friends have eaten at '+str(rname_monthly)+' over the past month'
			msg_end = ' of your friends have eaten healthy over the past month'
			categorize_messages(healthy_friends_monthly,total_friends,msg_end,1)
			msg = '<b>'+str(healthy_friends_monthly)+'</b> out of <b>'+str(total_friends)+'</b> of your friends have eaten healthy over the <b>past month</b>'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-delta).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,rid)
			if index_monthly:
				msg_end = ' of your friends have eaten'+str(w1_m)+' healthy '+str(desc_cuisine_monthly[index_monthly][0])+str(w1_m)+' over the past month'
				categorize_messages(desc_cuisine_monthly[index_monthly][1],total_friends,msg_end,1)
#				msg = ''+str(desc_cuisine_monthly[index_monthly][1])+' out of '+str(total_friends)+' of your friends have eaten'+str(w1_m)+' healthy '+str(desc_cuisine_monthly[index_monthly][0])+str(w1_m)+' over the past month'
#				print msg
			if spatial_index_monthly:
				msg_end = ' of your friends have eaten in '+str(dsorted_visits_spatial_monthly[spatial_index_monthly][0])+' over the past month'
				categorize_messages(dsorted_visits_spatial_monthly[spatial_index_monthly][1],total_friends,msg_end,1)
				msg = '<b>'+str(dsorted_visits_spatial_monthly[spatial_index_monthly][1])+'</b> out of <b> '+str(total_friends)+'</b> of your friends have eaten in <b>'+str(dsorted_visits_spatial_monthly[spatial_index_monthly][0])+'</b> over the past month'
				print msg
				cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-delta).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
				print cmd_str
				#insert_card(cmd_str,rid)
			
		else:
			#Not eaten cuisine weekly and monthly
			msg_end = 'of your friends have not eaten at '+str(rname_monthly)+' over the past month'
			categorize_messages(notvisited_monthly,total_friends,msg_end,-1)
#			msg = ''+str(int(percent_notvisited_monthly))+' % of your friends have not eaten at '+str(rname_monthly)+' over the past month'
#			print msg
#			print msg
		#	msg = ''+str(notvisited_monthly)+' out of '+str(total_friends)+' of your friends have not eaten at '+str(rname_monthly)+' over the past month'
		#	print msg
			msg_end = ' of your friends have not eaten healthy over the past month'
			categorize_messages(unhealthy_friends_monthly,total_friends,msg_end,-1)
#			msg = ''+str(unhealthy_friends_monthly)+' out of '+str(total_friends)+' of your friends have not eaten healthy over the past month'
#			print msg
			if spatial_index_monthly:
				msg_end = ' of your friends have not eaten in '+str(dsorted_visits_spatial_monthly[spatial_index_monthly][0])+' over the past month'
				categorize_messages(total_friends-dsorted_visits_spatial_monthly[spatial_index_monthly][1],total_friends,msg_end,-1)
#				msg = ''+str(total_friends-dsorted_visits_spatial_monthly[spatial_index_monthly][1])+' out of '+str(total_friends)+' of your friends have not eaten in '+str(dsorted_visits_spatial_monthly[spatial_index_monthly][0])+' over the past month'
#				print msg
		

def rest_visited_by_network(rid,msg_type,restaurant_name=""):
	cl = connect()
	all_restaurants_visited = {}
	all_network_healthy_visits = []
	all_network_healthy_visits_weekly = []
	all_network_healthy_visits_monthly = []
	steps_walked = 0 
	(epoch_week,epoch_month) = find_epoch_time()
	
	res1 = cl.command("select * from Person")
	total_people = len(res1)

	rest_visits = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(distinct(both('eats_at'))) from Person)")
	rest_visits_weekly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_week)+")")
	rest_visits_monthly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_month)+")")
	
	#for healthy visits needs work
	for i in range(total_people):
		userid = str(res1[i].rid)
	#	print "Processing"+str(userid)
	#	steps_walked += res1[i].steps_walked
		healthy_visits = cl.command("select name, res_id as res_id from (select expand(both('eats_at')) from Person where @rid = "+userid+")")
		healthy_visits_weekly = cl.command("select name, res_id as res_id from (select expand(in) from eats_at where created_at > "+str(epoch_week)+" and out="+userid+")")
		healthy_visits_monthly = cl.command("select name, res_id as res_id from (select expand(in) from eats_at where created_at > "+str(epoch_month)+" and out="+userid+")")
		all_network_healthy_visits.append(healthy_visits)
		all_network_healthy_visits_weekly.append(healthy_visits_weekly)
		all_network_healthy_visits_monthly.append(healthy_visits_monthly)

	if (check_data_existence([rest_visits])):
		print "Counting restaurant visits over all time"
		(all_restaurant_visits,asorted_all_restaurant_visits,dsorted_all_restaurant_visits) = count_visits(rest_visits)
		print "Counting cuisines eaten- all time"
		(cuisines_count,asc_cuisine,desc_cuisine) = count_cuisines_eaten([rest_visits])
		print "Counting healthy friends- all time"
		(healthy_users,unhealthy_users) = count_healthy_users(all_network_healthy_visits)
		print "Computing spatial stats"
		(visits_spatial,asorted_visits_spatial,dsorted_visits_spatial) = compute_spatial_stats([rest_visits])

		(visited_alltime,notvisited_alltime,percent_visited_alltime,percent_notvisited_alltime,rname_alltime) = calc_stats(total_people,dsorted_all_restaurant_visits)
		(index,w1,w2) = select_random_cuisine(desc_cuisine)
		if dsorted_visits_spatial:
			spatial_index = random.randrange(0,4)

		if (msg_type==1):
			msg = '<table><p><b>Top 3 restaurants visited</b></p><tr><td><b>Restaurant<b></td><td><b>Visits<b></td></tr><tr><td>'+get_restaurant_name(dsorted_all_restaurant_visits[0][0])+'</td><td>'+str(dsorted_all_restaurant_visits[0][1])+'</td></tr><tr><td>'+get_restaurant_name(dsorted_all_restaurant_visits[1][0])+'</td><td>'+str(dsorted_all_restaurant_visits[1][1])+'</td></tr><tr><td>'+get_restaurant_name(dsorted_all_restaurant_visits[2][0])+'</td><td>'+str(dsorted_all_restaurant_visits[2][1])+'</td></tr></table>'
			#msg = ''+get_restaurant_name(dsorted_all_restaurant_visits[i][0])+'\tVisits:'+ str(dsorted_all_restaurant_visits[i][1])
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=3))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			insert_card(cmd_str,rid)
			msg =  ''+' Most people in the network have visited <b>'+get_restaurant_name(dsorted_all_restaurant_visits[0][0])+'</b>'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=4))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,rid)

			msg = '<b>'+str(int(percent_visited_alltime))+'%</b> of the people in the network have eaten at <b>'+str(rname_alltime)+'</b>'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=5))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,rid)
			msg = ''+str(visited_alltime)+' out of '+str(total_people)+' of the people in the network have eaten at '+str(rname_alltime)
			print msg
			msg = ''+str(healthy_users)+' out of '+str(total_people)+' of the people in the network have eaten healthy'
			print msg
			msg = ''+str(desc_cuisine[index][1])+' out of '+str(total_people)+' of the people in the network have eaten healthy '+str(desc_cuisine[index][0])
			
			print msg
			if spatial_index:
				msg = '<b>'+str(dsorted_visits_spatial[spatial_index][1])+'</b> out of <b>'+str(total_people)+'</b> of the people in the network have eaten in <b>'+str(dsorted_visits_spatial[spatial_index][0])
				print msg
				cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
				print cmd_str
				insert_card(cmd_str,rid)
			msg = 'The people in the network have walked a total of '+str(steps_walked)+' steps'
			print msg
			msg = walking_message(steps_walked,"If you and the network on an average walk",total_people)
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=1))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,rid)
		else:
			msg = get_restaurant_name(asorted_all_restaurant_visits[0][0])+' was least popular among the people in the network '
			print msg
			msg = '<b>'+str(int(percent_notvisited_alltime))+'</b> % of the people in the network have <b>not</b> eaten at <b>'+str(rname_alltime)+'</b>'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=4))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,rid)
			msg =  ''+str(notvisited_alltime)+' out of '+str(total_people)+' of the people in the network have not eaten at '+str(rname_alltime)
			print msg
			msg = ''+str(unhealthy_users)+' out of '+str(total_people)+' of the people in the network have not eaten healthy'
			print msg
			msg = ''+str(total_people-desc_cuisine[index][1])+' out of '+str(total_people)+' of the people in the network have not eaten healthy '+str(desc_cuisine[index][0])
			print msg
			if spatial_index:
				msg = ''+str(total_people-dsorted_visits_spatial[spatial_index][1])+' out of '+str(total_people)+' of the people in the network have not eaten in '+str(dsorted_visits_spatial[spatial_index][0])
				print msg

			

	if (check_data_existence([rest_visits_weekly])):
		print "Counting weekly visits"
		(weekly_all_restaurant_visits,asorted_weekly_all_restaurant_visits,dsorted_weekly_all_restaurant_visits) = count_visits(rest_visits_weekly)
		print "Cuisines eaten weekly"
		(cuisines_count_weekly,asc_cuisine_weekly,desc_cuisine_weekly) = count_cuisines_eaten([rest_visits_weekly])
		print "Counting healthy friends- weekly"
		(healthy_users_weekly,unhealthy_users_weekly) = count_healthy_users(all_network_healthy_visits_weekly)	
		print "Computing spatial stats weekly"
		(visits_spatial_weekly,asorted_visits_spatial_weekly,dsorted_visits_spatial_weekly) = compute_spatial_stats([rest_visits_weekly])
		(visited_weekly,notvisited_weekly,percent_visited_weekly,percent_notvisited_weekly,rname_weekly) = calc_stats(total_people,dsorted_weekly_all_restaurant_visits)
		(index_weekly,w1_w,w2_w) = select_random_cuisine(desc_cuisine_weekly)
		if dsorted_visits_spatial_weekly:
			spatial_index_weekly = random.randrange(0,4)
		if (msg_type==1):
			msg = ''+str(int(percent_visited_weekly))+' % of the people in the network have eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = ''+str(visited_weekly)+' out of '+str(total_people)+' of the people in the network have eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = '<b>'+str(healthy_users_weekly)+'</b> out of <b>'+str(total_people)+'</b> of the people in the network have eaten healthy over the past week'
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=9))).strftime('%s'))*1000-15000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,rid)

			print msg
			msg = ''+str(desc_cuisine_weekly[index_weekly][1])+' out of '+str(total_people)+' of the people in the network have eaten healthy '+str(desc_cuisine_weekly[index_weekly][0])+' over the past week'
			print msg
			tags = ["healthy","chinese"]
				ret_val = begin_localimg(msg.replace("1 times","once"),"namedfriend_overlay_cuisine_monthly.jpg")
				if ret_val == 1:
					recid_img = create_binary_data("/Local/Users/dev/NetworkLabs/namedfriend_overlay_cuisine_monthly.jpg")
					cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",image="'+recid_img+'"'
					card_rid = insert_card(cmd_str,user_id,1)
					id_rec = cl.command('create edge has_uploaded_image from '+str(card_rid)+' to '+str(recid_img))
					print id_rec[0].rid	
			if spatial_index_weekly:
				msg = ''+str(dsorted_visits_spatial_weekly[spatial_index_weekly][1])+' out of '+str(total_people)+' of the people in the network have eaten in '+str(dsorted_visits_spatial_weekly[spatial_index_weekly][0])
				print msg


		else:
			msg = ''+str(int(percent_notvisited_weekly))+' % of the people in the network have not eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = ''+str(notvisited_weekly)+' out of '+str(total_people)+' of the people in the network have not eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = ''+str(unhealthy_users_weekly)+' out of '+str(total_people)+' of the people in the network have not eaten healthy over the past week'
			print msg
			if spatial_index_weekly:
				msg = ''+str(total_people-dsorted_visits_spatial_weekly[spatial_index_weekly][1])+' out of '+str(total_people)+' of the people in the network have not eaten in '+str(dsorted_visits_spatial_weekly[spatial_index_weekly][0])+' over the past week'
				print msg


	if (check_data_existence([rest_visits_monthly])):
		print "Counting monthly visits"
		(monthly_all_restaurant_visits,asorted_monthly_all_restaurant_visits,dsorted_monthly_all_restaurant_visits) = count_visits(rest_visits_monthly)
		print "Cuisines eaten monthly"
		(cuisines_count_monthly,asc_cuisine_monthly,desc_cuisine_monthly) = count_cuisines_eaten([rest_visits_monthly])
		print "Counting healthy friends- monthly"
		(healthy_users_monthly,unhealthy_users_monthly) = count_healthy_users(all_network_healthy_visits_monthly)
		print "Computing spatial stats monthly"
		(visits_spatial_monthly,asorted_visits_spatial_monthly,dsorted_visits_spatial_monthly) = compute_spatial_stats([rest_visits_monthly])

		(visited_monthly,notvisited_monthly,percent_visited_monthly,percent_notvisited_monthly,rname_monthly) = calc_stats(total_people,dsorted_monthly_all_restaurant_visits)
		(index_monthly,w1_m,w2_m) = select_random_cuisine(desc_cuisine_monthly)
		if dsorted_visits_spatial_monthly:
			spatial_index_monthly = random.randrange(0,4)

		if msg_type == 1:	
			msg = ''+str(int(percent_visited_monthly))+' % of the people in the network have eaten at '+str(rname_monthly)+' over the past month'
			print msg
			msg = ''+str(visited_monthly)+' out of '+str(total_people)+' of the people in the network have eaten at '+str(rname_monthly)+' over the past month'
			print msg
			msg = ''+str(healthy_users_monthly)+' out of '+str(total_people)+' of the people in the network have eaten healthy over the past month'
			print msg
			msg = '<b>'+str(desc_cuisine_monthly[index_monthly][1])+'</b> out of <b>'+str(total_people)+'</b> of the people in the network have eaten healthy '+str(desc_cuisine_monthly[index_monthly][0])+' over the <b>past month</b>'
			print msg
			if spatial_index_monthly:
				msg = ''+str(dsorted_visits_spatial_monthly[spatial_index_monthly][1])+' out of '+str(total_people)+' of the people in the network have eaten in '+str(dsorted_visits_spatial_monthly[spatial_index_monthly][0])+' over the past month'
				print msg
		else:
			msg = ''+str(int(percent_notvisited_monthly))+' % of the people in the network have not eaten at '+str(rname_monthly)+' over the past month'
			print msg
			msg = ''+str(notvisited_monthly)+' out of '+str(total_people)+' of the people in the network have not eaten at '+str(rname_monthly)+' over the past month'
			print msg
			msg = ''+str(unhealthy_users_monthly)+' out of '+str(total_people)+' of the people in the network have not eaten healthy over the past month'
			print msg
			if spatial_index_monthly:
				msg = ''+str(total_people-dsorted_visits_spatial_monthly[spatial_index_monthly][1])+' out of '+str(total_people)+' of the people in the network have not eaten in '+str(dsorted_visits_spatial_monthly[spatial_index_monthly][0])+' over the past month'
				print msg



def rest_visited_similar_pref(rid,rest_name=""):
#	print "In rest visited by similar pref"
	cl = connect()
	all_restaurants_visited = {}
#	print rid
	res1 = cl.command("select is_vegetarian,major,year from Person where @rid="+str(rid))
	vegetarian = res1[0].is_vegetarian
	major = res1[0].major
	year = res1[0].year
#	print vegetarian
#	print type(vegetarian)
#	print major
#	print year
#	if vegetarian==True:
#		rest_visited_by_vegetarians(rid,vegetarian,1,rest_name)
#		rest_visited_by_vegetarians(rid,vegetarian,-1,rest_name)

	rest_visited_by_majoryear(rid,major,year,rest_name,1)
	rest_visited_by_majoryear(rid,major,year,rest_name,-1)



def queries(user_id):
	(epoch_week,epoch_month) = find_epoch_time()

	rest_visits = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisine) as cuisine from (select expand(both('eats_at')) from Person where @rid = "+user_id+")")

	rest_visits_weekly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_week)+" and out="+user_id+")")

	rest_visits_monthly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_month)+" and out="+user_id+")")

	healthy_visits = cl.command("select name, res_id as res_id from (select expand(both('eats_at')) from Person where @rid = "+user_id+")")

	healthy_visits_weekly = cl.command("select name, res_id as res_id from (select expand(in) from eats_at where created_at > "+str(epoch_week)+" and out="+user_id+")")

	healthy_visits_monthly = cl.command("select name, res_id as res_id from (select expand(in) from eats_at where created_at > "+str(epoch_month)+" and out="+user_id+")")
	
	return (rest_visits,rest_visits_weekly,rest_visits_monthly,healthy_visits,healthy_visits_weekly,healthy_visits_monthly)

def process_query_alltime(all_visits,all_healthy_visits,all_visits_cuisine,all_visits_spatial):
	print "Counting visits over all time"
	(rest_visit,asc_rest_visit,desc_rest_visit) = count_restaurants_visited(all_visits)
	print "Counting healthy visits"
	(healthy_users,unhealthy_users) = count_healthy_users(all_healthy_visits)
	print "Counting cuisines eaten over all time"
	(cuisines_count,asc_cuisine,desc_cuisine) = count_cuisines_eaten(all_visits_cuisine)
	print "Computing spatial stats"
	(visits_spatial,asorted_visits_spatial,desc_visits_spatial) = compute_spatial_stats(all_visits_spatial)
	
	return (rest_visit,desc_rest_visit,healthy_users,unhealthy_users,cuisines_count,desc_cuisine,visits_spatial,desc_visits_spatial)

def process_query_weekly(all_visits_weekly,all_healthy_visits_weekly,all_visits_weekly_cuisine,all_visits_weekly_spatial):
	print "Counting weekly visits"
	(week_rest_visit,week_asc_rest_visit,week_desc_rest_visit) = count_restaurants_visited(all_visits_weekly)
	print "Counting healthy visits weekly"
	(healthy_users_weekly,unhealthy_users_weekly) = count_healthy_users(all_healthy_visits_weekly)
	print "Cuisines eaten weekly"
	(cuisines_count_weekly,asc_cuisine_weekly,desc_cuisine_weekly) = count_cuisines_eaten(all_visits_weekly_cuisine)
	print "Computing spatial stats weekly"
	(visits_spatial_weekly,asorted_visits_spatial_weekly,desc_visits_spatial_weekly) = compute_spatial_stats(all_visits_weekly_spatial)
	return (week_rest_visit,week_desc_rest_visit,healthy_users_weekly,unhealthy_users_weekly,cuisines_count_weekly,desc_cuisine_weekly,visits_spatial_weekly,desc_visits_spatial_weekly)   
	
def process_query_monthly(all_visits_monthly,all_healthy_visits_monthly,all_visits_monthly_cuisine,all_visits_monthly_spatial):
	print "Counting monthly visits"
	(month_rest_visit,month_asc_rest_visit,month_desc_rest_visit) = count_restaurants_visited(all_visits_monthly)
	print "Counting healthy visits monthly"
	(healthy_users_monthly,unhealthy_users_monthly) = count_healthy_users(all_healthy_visits_monthly)
	print "Cuisines eaten monthly"
	(cuisines_count_monthly,asc_cuisine_monthly,desc_cuisine_monthly) = count_cuisines_eaten(all_visits_monthly_cuisine)
	print "Computing spatial stats monthly"
	(visits_spatial_monthly,asorted_visits_spatial_monthly,desc_visits_spatial_monthly) = compute_spatial_stats(all_visits_monthly_spatial)
	return (month_rest_visit,month_desc_rest_visit,healthy_users_monthly,unhealthy_users_monthly,cuisines_count_monthly,desc_cuisine_monthly,visits_spatial_monthly,desc_visits_spatial_monthly)

def select_random_cuisine(cuisines_eaten):
	len_visits = len(cuisines_eaten)
	index_cuisine = random.randrange(0,len_visits)

	cuisine_places = ['bars','streetvendors','Cheese Shops','delis','divebars','arcades','Wine & Spirits','poolhalls','ethnicmarkets','pubs','diners','lounges','sportsbars','bakeries','cafes','seafoodmarkets','Delis','restaurants','creperies']
	cuisine_types = ['mexican','chinese','mediterranean','japanese','tradamerican','spanish','hotdog','newamerican','indpak','vietnamese','asianfusion','korean','tex-mex','cajun','latin','southern','vegan','gluten_free','mongolian','thai','malaysian','greek','szechuan','mideastern','argentine','vegetarian','irish','italian']
	food = ['sushi','soup','Sandwiches','hotdog','chicken_wings','fishnchips','burgers','buffets','icecream','sandwiches','soulfood','bbq','pizza','cheesesteaks','chocolate','coffee','hotdogs','salad','gelato','breakfast_brunch','steak','seafood']
#	print cuisines_eaten[index_cuisine][0]
	if cuisines_eaten[index_cuisine][0] in cuisine_places:
		word1 = ' at '
		word2 = ' '
	elif cuisines_eaten[index_cuisine][0] in cuisine_types:
		word1 = ' '
		word2 = ' food '
	else:
		word1 = ' '
		word2 = ' '
	
	return (index_cuisine,word1,word2)

def rest_visited_by_vegetarians(rid,veg,msg_type,restaurant_name):
	restaurant_veg_visits ={}
	msg = ""
	steps_walked = 0
	all_veg_rest_visits = []
	all_veg_healthy_visits = []
	all_veg_rest_visits_weekly = []
	all_veg_rest_visits_monthly = []
	all_veg_healthy_visits_weekly = []
	all_veg_healthy_visits_monthly = []
	all_veg_spatial_stats = []
	all_veg_spatial_stats_weekly = []
	all_veg_spatial_stats_monthly = []

	cl = connect()
	vegetarians = cl.command("select * from Person where is_vegetarian="+str(veg))
	total_veg = len(vegetarians)
	
	for i in xrange(total_veg):
		vegid = str(vegetarians[i].rid)
		steps_walked += vegetarians[i].steps_walked
		(veg_rest_visits,veg_rest_visits_weekly,veg_rest_visits_monthly,veg_healthy_visits,veg_healthy_visits_weekly,veg_healthy_visits_monthly) = queries(vegid)
		all_veg_rest_visits.append(veg_rest_visits)
		all_veg_healthy_visits.append(veg_healthy_visits)
		all_veg_rest_visits_weekly.append(veg_rest_visits_weekly)
		all_veg_rest_visits_monthly.append(veg_rest_visits_monthly)
		all_veg_healthy_visits_weekly.append(veg_healthy_visits_weekly)
		all_veg_healthy_visits_monthly.append(veg_healthy_visits_monthly)
		

	if (check_data_existence(all_veg_rest_visits)):
		print "Finding stats vegetarians- all aggregates"	
		(veg_visits,veg_desc_visits,healthy_veg,unhealthy_veg,veg_cuisine_count,veg_desc_cuisine,veg_spatial,veg_desc_spatial) = process_query_alltime(all_veg_rest_visits,all_veg_healthy_visits,all_veg_rest_visits,all_veg_rest_visits)
		(visited_alltime,notvisited_alltime,percent_visited_alltime,percent_notvisited_alltime,rname_alltime) = calc_stats(total_veg,veg_desc_visits)
		(index,w1,w2) = select_random_cuisine(veg_desc_cuisine)
		if veg_desc_spatial:
			spatial_index = random.randrange(0,4)
		if msg_type==1:
			msg = '<table><p>Top 3 restaurants vegetarians visited</p><tr><td><b>Restaurant Name</b></td><td><b>Visits</b></td></tr><tr><td>'+get_restaurant_name(veg_desc_visits[0][0])+'</td><td>'+str(veg_desc_visits[0][1])+'</td></tr><tr><td>'+get_restaurant_name(veg_desc_visits[1][0])+'</td><td>'+str(veg_desc_visits[1][1])+'</td></tr><tr><td>'+get_restaurant_name(veg_desc_visits[2][0])+'</td><td>'+str(veg_desc_visits[2][1])+'</td></tr></table>'
			print msg
			cmd_str = 'create vertex Card set type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000-20000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,rid)			

			msg = ''+str(int(percent_visited_alltime))+' % of the vegetarians have eaten at '+str(rname_alltime)
			print msg
			msg = ''+str(visited_alltime)+' out of '+str(total_veg)+' of the vegetarians have eaten at '+str(rname_alltime)
			print msg
			msg = ''+str(healthy_veg)+' out of '+str(total_veg)+' of the vegetarians have eaten healthy'
			print msg
			msg = ''+str(veg_desc_cuisine[index][1])+' out of '+str(total_veg)+' of the vegetarians have eaten'+str(w1)+'healthy '+str(veg_desc_cuisine[index][0])+str(w2)
			print msg
			tags = ["healthy","chinese"]
			ret_val = begin_localimg(msg.replace("1 times","once"),"namedfriend_overlay_cuisine_monthly.jpg")
			if ret_val == 1:
					recid_img = create_binary_data("/Local/Users/dev/NetworkLabs/namedfriend_overlay_cuisine_monthly.jpg")
					cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",image="'+recid_img+'"'
			#		card_rid = insert_card(cmd_str,user_id,1)
			#		id_rec = cl.command('create edge has_uploaded_image from '+str(card_rid)+' to '+str(recid_img))
			#		print id_rec[0].rid	

			if spatial_index:
				msg = ''+str(veg_desc_spatial[spatial_index][1])+' out of '+str(total_veg)+' of the vegetarians have eaten in '+str(veg_desc_spatial[spatial_index][0])
				print msg
			msg = 'Your friends have walked a total of '+str(steps_walked)+' steps'
			print msg
			msg = walking_message(steps_walked,"If you and the other vegetarians in the network walk",total_veg)
			print msg
		else:
			msg = ''+str(int(percent_notvisited_alltime))+' % of the vegetarians have not eaten at '+str(rname_alltime)
			print msg
			msg =  ''+str(notvisited_alltime)+' out of '+str(total_veg)+' of the vegetarians have not eaten at '+str(rname_alltime)
			print msg
			msg = ''+str(unhealthy_veg)+' out of '+str(total_veg)+' of the vegetarians have not eaten healthy'
			print msg
			msg = ''+str(total_veg-veg_desc_cuisine[index][1])+' out of '+str(total_veg)+' of the vegetarians have not eaten healthy '+str(veg_desc_cuisine[index][0])
			print msg
			if spatial_index:
				msg = ''+str(total_veg-veg_desc_spatial[spatial_index][1])+' out of '+str(total_veg)+' of the vegetarians have not eaten in '+str(veg_desc_spatial[spatial_index][0])
				print msg
			
		
	if (check_data_existence(all_veg_rest_visits_weekly)):
		print "Finding stats- weekly aggregates"
		(veg_week_visits,veg_week_desc_visits,healthy_veg_weekly,unhealthy_veg_weekly,veg_cuisines_count_weekly,veg_desc_cuisine_weekly,veg_spatial_weekly,veg_desc_spatial_weekly) = process_query_weekly(all_veg_rest_visits_weekly,all_veg_healthy_visits_weekly,all_veg_rest_visits_weekly,all_veg_rest_visits_weekly)
		(visited_weekly,notvisited_weekly,percent_visited_weekly,percent_notvisited_weekly,rname_weekly) = calc_stats(total_veg,veg_week_desc_visits)
#		(index,index_weekly,index_monthly,w1,w2,w1_w,w2_w,w1_m,w2_m) = select_random_cuisine(veg_desc_cuisine,veg_desc_cuisine_weekly,veg_desc_cuisine_monthly)
		(index_weekly,w1_w,w2_w) = select_random_cuisine(veg_desc_cuisine_weekly)
		if veg_desc_spatial_weekly:
			spatial_index_weekly = random.randrange(0,4)

		if msg_type==1:
			msg = ''+str(int(percent_visited_weekly))+' % of the vegetarians have eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = ''+str(visited_weekly)+' out of '+str(total_veg)+' of the vegetarians have eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = ''+str(healthy_veg_weekly)+' out of '+str(total_veg)+' of the vegetarians have eaten healthy over the past week'
			print msg
			msg = ''+str(veg_desc_cuisine_weekly[index_weekly][1])+' out of '+str(total_veg)+' of the vegetarians have eaten'+str(w1_w)+'healthy '+str(veg_desc_cuisine_weekly[index_weekly][0])+str(w2_w)+' over the past week'
			print msg
			if spatial_index_weekly:
				msg = ''+str(veg_desc_spatial_weekly[spatial_index_weekly][1])+' out of '+str(total_veg)+' of the vegetarians have eaten in '+str(veg_desc_spatial[spatial_index][0])+' over the past week'
				print msg

		else:
			msg = ''+str(int(percent_notvisited_weekly))+' % of the vegetarians have not eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = ''+str(notvisited_weekly)+' out of '+str(total_veg)+' of the vegetarians have not eaten at '+str(rname_weekly)+' over the past week'
			print msg
			msg = ''+str(unhealthy_veg_weekly)+' out of '+str(total_veg)+' of the vegetarians have not eaten healthy over the past week'
			print msg
			if spatial_index_weekly:
				msg = ''+str(total_veg-veg_desc_spatial_weekly[spatial_index_weekly][1])+' out of '+str(total_veg)+' of the vegetarians have not eaten in '+str(veg_desc_spatial[spatial_index_weekly][0])+' over the past week'
				print msg

	if (check_data_existence(all_veg_rest_visits_monthly)):
		print "Finding stats- monthly aggregates"
		(veg_month_visits,veg_month_desc_visits,healthy_veg_monthly,unhealthy_veg_monthly,veg_cuisines_count_monthly,veg_desc_cuisine_monthly,veg_spatial_monthly,veg_desc_spatial_monthly) = process_query_monthly(all_veg_rest_visits_monthly,all_veg_healthy_visits_monthly,all_veg_rest_visits_monthly,all_veg_rest_visits_monthly)
		(visited_monthly,notvisited_monthly,percent_visited_monthly,percent_notvisited_monthly,rname_monthly) = calc_stats(total_veg,veg_month_desc_visits)
		(index_monthly,w1_m,w2_m) = select_random_cuisine(veg_desc_cuisine_monthly)
		if veg_desc_spatial_monthly:
			spatial_index_monthly = random.randrange(0,4) 
		if msg_type == 1:
			msg = ''+str(int(percent_visited_monthly))+' % of the vegetarians have eaten at '+str(rname_monthly)+' over the past month'
			print msg
			msg = ''+str(visited_monthly)+' out of '+str(total_veg)+' of the vegetarians have eaten at '+str(rname_monthly)+' over the past month'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000-17000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			insert_card(cmd_str,rid)
		
			msg = ''+str(healthy_veg_monthly)+' out of '+str(total_veg)+' of the vegetarians have eaten healthy over the past month'
			print msg
		
			msg = ''+str(veg_desc_cuisine_monthly[index_monthly][1])+' out of '+str(total_veg)+' of the vegetarians have eaten'+str(w1_m)+ 'healthy '+str(veg_desc_cuisine_monthly[index_monthly][0])+str(w2_m)+' over the past month'
			print msg
			if spatial_index_monthly:
				msg = ''+str(veg_desc_spatial_monthly[spatial_index_monthly][1])+' out of '+str(total_veg)+' of the vegetarians have eaten in '+str(veg_desc_spatial_monthly[spatial_index_monthly][0])+' over the past month'
				print msg
			
		else:
		
			msg = ''+str(int(percent_notvisited_monthly))+' % of the vegetarians have not eaten at '+str(rname_monthly)+' over the past month'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000-11000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			insert_card(cmd_str,rid)

			msg = ''+str(notvisited_monthly)+' out of '+str(total_veg)+' of the vegetarians have not eaten at '+str(rname_monthly)+' over the past month'
			print msg

			msg = ''+str(unhealthy_veg_monthly)+' out of '+str(total_veg)+' of the vegetarians have not eaten healthy over the past month'
			print msg
			if spatial_index_monthly:
				msg = ''+str(total_veg-veg_desc_spatial_monthly[spatial_index_monthly][1])+' out of '+str(total_veg)+' of the vegetarians have not eaten in '+str(veg_desc_spatial_monthly[spatial_index_monthly][0])+' over the past month'
				print msg


def rest_visited_by_majoryear(rid,majors,year,restaurant_name,msg_type):
	#print veg
	restaurant_major_visits ={}
	cl = connect()
	msg = []
	cmd_str = 'select * from Person where major="'+str(majors)+'" and year="'+str(year)+'"'
	major = cl.command(cmd_str)
	total_major = len(major)
	steps_walked = 0
	all_major_rest_visits = []
	all_major_healthy_visits = []
	all_major_rest_visits_weekly = []
	all_major_rest_visits_monthly = []
	all_major_healthy_visits_weekly = []
	all_major_healthy_visits_monthly = []

	for i in xrange(total_major):
		majorid = str(major[i].rid)
		#steps_walked += major[i].steps_walked
		(major_rest_visits,major_rest_visits_weekly,major_rest_visits_monthly,major_healthy_visits,major_healthy_visits_weekly,major_healthy_visits_monthly) = queries(majorid)
		all_major_rest_visits.append(major_rest_visits)
		all_major_healthy_visits.append(major_healthy_visits)
		all_major_rest_visits_weekly.append(major_rest_visits_weekly)
		all_major_rest_visits_monthly.append(major_rest_visits_monthly)
		all_major_healthy_visits_weekly.append(major_healthy_visits_weekly)
		all_major_healthy_visits_monthly.append(major_healthy_visits_monthly)

	if (check_data_existence(all_major_rest_visits)):
		print "Finding stats- all aggregates"	
		(major_visits,major_desc_visits,healthy_major,unhealthy_major,major_cuisine_count,major_desc_cuisine,major_spatial,major_desc_spatial) = process_query_alltime(all_major_rest_visits,all_major_healthy_visits,all_major_rest_visits,all_major_rest_visits)
		(visited_alltime,notvisited_alltime,percent_visited_alltime,percent_notvisited_alltime,rname_alltime) = calc_stats(total_major,major_desc_visits)
		if rname_alltime:
			(index,w1,w2) = select_random_cuisine(major_desc_cuisine)
			if major_desc_spatial:
				spatial_index = random.randrange(0,4)
			if (msg_type==1):
				print len(major_desc_visits)
				if len(major_desc_visits)>=3:
					print major_desc_visits
					print majors
					msg = '<table><p>Top 3 restaurants' +str(majors)+str(year)+'students visited</p><tr><td><b>Restaurant Name</b></td><td><b>Visits</b></td></tr><tr><td>'+get_restaurant_name(major_desc_visits[0][0])+'</td><td>'+str(major_desc_visits[0][1])+'</td></tr><tr><td>'+get_restaurant_name(major_desc_visits[1][0])+'</td><td>'+str(major_desc_visits[1][1])+'</td></tr><tr><td>'+get_restaurant_name(major_desc_visits[2][0])+'</td><td>'+str(major_desc_visits[2][1])+'</td></tr></table>'
			#msg = ''+get_restaurant_name(dsorted_all_restaurant_visits[i][0])+'\tVisits:'+ str(dsorted_all_restaurant_visits[i][1])
					print msg
					cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
					print cmd_str
#					insert_card(cmd_str,rid)			
				msg = ''+str(int(percent_visited_alltime))+' % of '+str(majors)+' '+str(year)+' students have eaten at '+str(rname_alltime)
				print msg

				msg = ''+str(visited_alltime)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten at '+str(rname_alltime)
				print msg

				msg = ''+str(healthy_major)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten healthy'
				print msg
				msg = ''+str(major_desc_cuisine[index][1])+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten'+str(w1)+'healthy'+str(major_desc_cuisine[index][0])+str(w2)
				print msg
				msg = 'Your friends have walked a total of '+str(steps_walked)+' steps'
				print msg
				msg = walking_message(steps_walked,str('If you and the other '+str(majors)+' '+str(year)+'students walk'),total_major)
				print msg			
				if spatial_index:
					msg = ''+str(major_desc_spatial[spatial_index][1])+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students have eaten in '+str(major_desc_spatial[spatial_index][0])
					print msg

			else:
				msg = ''+str(int(percent_notvisited_alltime))+' % of the of '+str(majors)+' '+str(year)+' students have not eaten at '+str(rname_alltime)
				print msg
				msg =  ''+str(notvisited_alltime)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have not eaten at '+str(rname_alltime)
				print msg
				msg = ''+str(unhealthy_major)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have not eaten healthy'
				print msg

				msg = '<b>'+str(total_major-major_desc_cuisine[index][1])+'</b> out of <b>'+str(total_major)+'</b> of the <b>'+str(majors)+' '+str(year)+'</b> students have not eaten healthy<b> '+str(major_desc_cuisine[index][0])+'</b>'
				print msg
				cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
				print cmd_str
				insert_card(cmd_str,rid)
		#	print str(asorted_restaurant_veg_visits[0][0])+' was least popular among vegetarians '
				if spatial_index:
					msg = ''+str(total_major-major_desc_spatial[spatial_index][1])+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students have not eaten in '+str(major_desc_spatial[spatial_index][0])
					print msg

	if (check_data_existence(all_major_rest_visits_weekly)):
		print "Finding stats- weekly aggregates"
		(major_week_visits,major_week_desc_visits,healthy_major_weekly,unhealthy_major_weekly,major_cuisines_count_weekly,major_desc_cuisine_weekly,major_spatial_weekly,major_desc_spatial_weekly) = process_query_weekly(all_major_rest_visits_weekly,all_major_healthy_visits_weekly,all_major_rest_visits_weekly,all_major_rest_visits_weekly)
		(visited_weekly,notvisited_weekly,percent_visited_weekly,percent_notvisited_weekly,rname_weekly) = calc_stats(total_major,major_week_desc_visits)
		#(index,index_weekly,index_monthly,w1,w2,w1_w,w2_w,w1_m,w2_m) = select_random_cuisine(major_desc_cuisine,major_desc_cuisine_weekly,major_desc_cuisine_monthly)
		if rname_weekly:
			(index_weekly,w1_w,w2_w) = select_random_cuisine(major_desc_cuisine_weekly)
			if major_desc_spatial_weekly:
				spatial_index_weekly = random.randrange(0,4)

			if (msg_type==1):
				msg = ''+str(int(percent_visited_weekly))+' % of the of '+str(majors)+' '+str(year)+' students have eaten at '+str(rname_weekly)+' over the past week'
				print msg
				msg = ''+str(visited_weekly)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten at '+str(rname_weekly)+' over the past week'
				print msg
				msg = '<b>'+str(healthy_major_weekly)+'</b> out of <b>'+str(total_major)+'</b> of the of <b>'+str(majors)+' '+str(year)+'</b> students have eaten healthy over the <b>past week</b>'
				print msg
				cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
				print cmd_str
			#	insert_card(cmd_str,rid)

				msg = ''+str(major_desc_cuisine_weekly[index_weekly][1])+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten'+str(w1_w)+' healthy '+str(major_desc_cuisine_weekly[index_weekly][0])+str(w2_w)+' over the past week'
			#	print msg
				if spatial_index_weekly:
					msg = ''+str(major_desc_spatial_weekly[spatial_index_weekly][1])+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students  have eaten in '+str(major_desc_spatial[spatial_index][0])+' over the past week'
					print msg
			

			else:
				msg = ''+str(int(percent_notvisited_weekly))+' % of the of '+str(majors)+' '+str(year)+' students have not eaten at '+str(rname_weekly)+' over the past week'
				print msg
				msg = ''+str(notvisited_weekly)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have not eaten at '+str(rname_weekly)+' over the past week'
				print msg
				msg = ''+str(unhealthy_major_weekly)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have not eaten healthy over the past week'
				print msg
				if spatial_index_weekly:
					msg = ''+str(total_major-major_desc_spatial_weekly[spatial_index_weekly][1])+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students have not eaten in '+str(major_desc_spatial[spatial_index_weekly][0])+' over the past week'
					print msg

	if (check_data_existence(all_major_rest_visits_monthly)):
		print "Finding stats- monthly aggregates"
		(major_month_visits,major_month_desc_visits,healthy_major_monthly,unhealthy_major_monthly,major_cuisines_count_monthly,major_desc_cuisine_monthly,major_spatial_monthly,major_desc_spatial_monthly) = process_query_monthly(all_major_rest_visits_monthly,all_major_healthy_visits_monthly,all_major_rest_visits_monthly,all_major_rest_visits_monthly)
		(visited_monthly,notvisited_monthly,percent_visited_monthly,percent_notvisited_monthly,rname_monthly) = calc_stats(total_major,major_month_desc_visits)
		if rname_monthly:
			(index_monthly,w1_m,w2_m) = select_random_cuisine(major_desc_cuisine_monthly)
			if major_desc_spatial_monthly:
				spatial_index_monthly = random.randrange(0,4) 
			if (msg_type==1):

				msg = ''+str(int(percent_visited_monthly))+' % of the of '+str(majors)+' '+str(year)+' students have eaten at '+str(rname_monthly)+' over the past month'
				print msg
				msg = ''+str(visited_monthly)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten at '+str(rname_monthly)+' over the past month'
				print msg
				msg = ''+str(healthy_major_monthly)+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten healthy over the past month'
				print msg
				msg = ''+str(major_desc_cuisine_monthly[index_monthly][1])+' out of '+str(total_major)+' of the of '+str(majors)+' '+str(year)+' students have eaten'+str(w1_m)+ 'healthy '+str(major_desc_cuisine_monthly[index_monthly][0].replace("_"," "))+str(w2_m)+' over the past month'
				print msg
			#	tags = ["healthy",str(major_desc_cuisine_monthly[index_monthly][0])]
				tags = ["healthy","chinese"]
				ret_val = begin_localimg(msg.replace("1 times","once"),"namedfriend_overlay_cuisine_monthly.jpg")
				if ret_val == 1:
					recid_img = create_binary_data("/Local/Users/dev/NetworkLabs/namedfriend_overlay_cuisine_monthly.jpg")
					cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",image="'+recid_img+'"'
					card_rid = insert_card(cmd_str,user_id,1)
					id_rec = cl.command('create edge has_uploaded_image from '+str(card_rid)+' to '+str(recid_img))
					print id_rec[0].rid	

				
				if spatial_index_monthly:
					msg = ''+str(major_desc_spatial_monthly[spatial_index_monthly][1])+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students have eaten in '+str(major_desc_spatial_monthly[spatial_index_monthly][0])+' over the past month'
					print msg
			else:
				msg = ''+str(int(percent_notvisited_monthly))+' % of the of '+str(majors)+' '+str(year)+' students have not eaten at '+str(rname_monthly)+' over the past month'
				print msg
				msg = ''+str(notvisited_monthly)+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students have not eaten at '+str(rname_monthly)+' over the past month'
				print msg
				msg = ''+str(unhealthy_major_monthly)+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students have not eaten healthy over the past month'
				print msg
				if spatial_index_monthly:
					msg = ''+str(total_major-major_desc_spatial_monthly[spatial_index_monthly][1])+' out of '+str(total_major)+' of the '+str(majors)+' '+str(year)+' students have not eaten in '+str(major_desc_spatial_monthly[spatial_index_monthly][0])+' over the past month'
					print msg
		
		
#generates statistics related to the named friend
## Friend has been eating healthy over the past month
## Friend has visited XXX 10 times
## Friend has visited XXx most number of times
## Graph showing friend's health index over the past week
## Compare health quotients



def gen_stats_named_friend(user_id,named_friend_rid,named_friend_name,steps_walked,msg_type,restaurant_name=""):
	#(named_friend_rid,named_friend_name) = get_strongest_tie_rest_visit(user_id)
#	print named_friend_rid
#	print named_friend_name
	visit_counts = {}	
	desc_visitcount = []
	asc_visitcount = []
	cl = connect()
	healthy_visits = 0
	unhealthy_visits = 0
	msg = []

	(epoch_week,epoch_month) = find_epoch_time()
	rest_visits = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(both('eats_at')) from Person where @rid ="+str(named_friend_rid)+")")
	#print str(visited_rest)

	rest_visits_weekly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_week)+" and out="+str(named_friend_rid)+")")
	rest_visits_monthly = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(in) from eats_at where created_at > "+str(epoch_month)+" and out="+str(named_friend_rid)+")")
	
	
	if rest_visits:
		(restaurant_visits,desc_visitcount,asc_visitcount) = count_visits(rest_visits)
		(healthy_visits,unhealthy_visits) = find_healthy_visits(restaurant_visits)
		print "Counting cuisines eaten- all time"
		(cuisines_count,asc_cuisine,desc_cuisine) = count_cuisines_eaten([rest_visits])
		if msg_type==1:
			msg = ''+str(named_friend_name)+' has visited '+get_restaurant_name(desc_visitcount[0][0])+' '+str(desc_visitcount[0][1])+' times'
			print msg
			msg = ''+str(named_friend_name)+' has visited '+get_restaurant_name(desc_visitcount[0][0])+' most times'
			print msg
			msg = ''+str(named_friend_name)+' has eaten healthy '+str(desc_cuisine[0][0])+' '+str(desc_cuisine[0][1])+' times'
			print msg
			msg = ''+str(named_friend_name)+' has walked a total of '+str(steps_walked)

			#how many times has the friend eaten healthy
			if unhealthy_visits==0:
				msg = ''+str(named_friend_name)+' has never eaten unhealthy'
			else: 
				msg = '<b>'+str(named_friend_name)+'</b> has eaten healthy food <b>'+str(healthy_visits)+'</b> times'		
				
		else:
			msg = ''+str(named_friend_name)+' has visited '+str(asc_visitcount[0][0])+' '+str(asc_visitcount[0][1])+' times'
			print msg
			msg = ''+str(named_friend_name)+' has visited '+str(asc_visitcount[0][0])+' least times'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int((creation_date-(datetime.timedelta(days=1))).strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			insert_card(cmd_str,rid)
			if healthy_visits==0:
				msg = ''+str(named_friend_name)+' has never eaten healthy'
			else:
				msg = ''+str(named_friend_name)+' has eaten unhealthy food '+str(unhealthy_visits)+' times'		
		
	if rest_visits_weekly:
		index_weekly = ""	
		(restaurant_visits_weekly,desc_visitcount_weekly,asc_visitcount_weekly) = count_visits(rest_visits_weekly)
		(healthy_visits_weekly,unhealthy_visits_weekly) = find_healthy_visits(restaurant_visits_weekly)
		print "Cuisines eaten weekly"
		(cuisines_count_weekly,asc_cuisine_weekly,desc_cuisine_weekly) = count_cuisines_eaten([rest_visits_weekly])
		if desc_cuisine_weekly:
			(index_weekly,w1_w,w2_w) = select_random_cuisine(desc_cuisine_weekly)

		if msg_type==1:
			msg = ''+str(named_friend_name)+' has visited '+get_restaurant_name(desc_visitcount_weekly[0][0])+' '+str(desc_visitcount_weekly[0][1])+' times over the past week'
			print msg
			msg = ''+str(named_friend_name)+' has visited '+get_restaurant_name(desc_visitcount_weekly[0][0])+' most times over the past week'
			print msg
			if index_weekly:
				msg = '<b>'+str(named_friend_name)+'</b> has eaten healthy <b>'+str(desc_cuisine_weekly[index_weekly][0])+' '+str(desc_cuisine_weekly[index_weekly][1])+'</b> times over the past week'
				print msg
				cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
	                        print cmd_str
        	#                insert_card(cmd_str,rid)
			if unhealthy_visits_weekly==0:
				msg = ''+str(named_friend_name)+' has never eaten unhealthy over the past week'
			else: 
				msg = ''+str(named_friend_name)+' has eaten healthy food '+str(healthy_visits_weekly)+' times over the past week'	

		else:
			msg = '<b>'+str(named_friend_name)+'</b> has visited <b>'+str(asc_visitcount_weekly[0][0])+' '+str(asc_visitcount_weekly[0][1])+'</b> times over the <b>past week</b>'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000-500)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,user_id)

			msg = ''+str(named_friend_name)+' has visited '+str(asc_visitcount_weekly[0][0])+' least times over the past week'
			print msg
			if healthy_visits_weekly==0:
				msg = ''+str(named_friend_name)+' has never eaten healthy over the past week'
			else: 
				msg = ''+str(named_friend_name)+' has eaten unhealthy food '+str(unhealthy_visits_weekly)+' times over the past week'

	if rest_visits_monthly:	
		(restaurant_visits_monthly,desc_visitcount_monthly,asc_visitcount_monthly) = count_visits(rest_visits_monthly)
		(healthy_visits_monthly,unhealthy_visits_monthly) = find_healthy_visits(restaurant_visits_monthly)
		print "Cuisines eaten monthly"
		(cuisines_count_monthly,asc_cuisine_monthly,desc_cuisine_monthly) = count_cuisines_eaten([rest_visits_monthly])
		(index_monthly,w1_m,w2_m) = select_random_cuisine(desc_cuisine_monthly)

		if msg_type==1:
			msg = ''+str(named_friend_name)+' has visited '+get_restaurant_name(desc_visitcount_monthly[0][0])+' '+str(desc_visitcount_monthly[0][1])+' times over the past month'
			print msg
			msg = '<b>'+str(named_friend_name)+'</b> has visited <b>'+get_restaurant_name(desc_visitcount_monthly[0][0])+'</b> most times over the <b>past month</b>'
			print msg
			cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg+'"'
			print cmd_str
			#insert_card(cmd_str,user_id)
			print desc_cuisine_monthly
			if desc_cuisine_monthly:
				msg = ''+str(named_friend_name)+' has eaten healthy '+str(desc_cuisine_monthly[index_monthly][0])+' '+str(desc_cuisine_monthly[index_monthly][1])+' times over the past month'
				print msg
				#tags = ["healthy",str(desc_cuisine_monthly[0][0])]
				tags = ["healthy","chinese"]
				ret_val = begin_localimg(msg.replace("1 times","once"),"namedfriend_overlay_cuisine_monthly.jpg")
				if ret_val == 1:
					recid_img = create_binary_data("/Local/Users/dev/NetworkLabs/namedfriend_overlay_cuisine_monthly.jpg")
					cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",image="'+recid_img+'"'
					card_rid = insert_card(cmd_str,user_id,1)
					id_rec = cl.command('create edge has_uploaded_image from '+str(card_rid)+' to '+str(recid_img))
					print id_rec[0].rid			
			if unhealthy_visits_monthly==0:
				msg = ''+str(named_friend_name)+' has never eaten unhealthy over the past month'
			else: 
				msg = ''+str(named_friend_name)+' has eaten healthy food '+str(healthy_visits_monthly)+' times over the past month'
			
		else:
			msg = ''+str(named_friend_name)+' has visited '+str(asc_visitcount_monthly[0][0])+' '+str(asc_visitcount_monthly[0][1])+' times over the past month'
			print msg
			msg = ''+str(named_friend_name)+' has visited '+str(asc_visitcount_monthly[0][0])+' least times over the past month'
			print msg
			if healthy_visits_monthly==0:
				msg = ''+str(named_friend_name)+' has never eaten healthy over the past month'
			else: 
				msg = ''+str(named_friend_name)+' has eaten unhealthy food '+str(unhealthy_visits_monthly)+' times over the past month'
def get_monthly_stats(user_id):
	cl = connect()
	current_epoch_time = int(time.time())

	week1 = current_epoch_time*1000 - 604800000*4
	week2 = current_epoch_time*1000 - 604800000*3
	week3 = current_epoch_time*1000 - 604800000*2
	week4 = current_epoch_time*1000 - 604800000
	rest_visits_week1 = cl.command("select count(distinct(res_id)) from (select expand(in) from eats_at where created_at >= "+str(week1)+" and created_at < "+str(week2)+" and out="+str(user_id)+")")
	rest_visits_week2 = cl.command("select count(distinct(res_id)) from (select expand(in) from eats_at where created_at >= "+str(week2)+" and created_at < "+str(week3)+" and out="+str(user_id)+")")
	rest_visits_week3 = cl.command("select count(distinct(res_id)) from (select expand(in) from eats_at where created_at >= "+str(week3)+" and created_at < "+str(week4)+" and out="+str(user_id)+")")
	rest_visits_week4 = cl.command("select count(distinct(res_id)) from (select expand(in) from eats_at where created_at >= "+str(week4)+" and created_at < "+str(current_epoch_time)+" and out="+str(user_id)+")")
	visit_list = [rest_visits_week1[0].count,rest_visits_week2[0].count,rest_visits_week3[0].count,rest_visits_week4[0].count]
	return visit_list	

#return friend name and friend rid
def get_strongest_tie_rest_visit(user_id):
   # print str(user_id)
    cl = connect()
    cmd_all_user_tie = "select @rid,weight,in as incoming from similar_to where out="+str(user_id)+" order by weight desc"
    #print str(cmd_all_user_tie)
    #cmd_all_user_tie = "select @rid,weight,in as incoming from similar_to where out=#12:6121 order by weight desc"
    all_user_tie = cl.command(cmd_all_user_tie)
   # print len(all_user_tie)
    if len(all_user_tie)>2:
    	strongest_tie_rid = all_user_tie[0].incoming
#	print strongest_tie_rid
    	cmd_str_tie_name = "Select first_name,steps_walked from Person where @rid="+str(strongest_tie_rid)
	strongest_tie = cl.command(cmd_str_tie_name)
	strongest_tie_name =  strongest_tie[0].first_name
	steps = strongest_tie[0].steps_walked
#	print "Rid of the strongest tie"+ str(strongest_tie_rid)
#	print "Name of the strongest tie" + str(strongest_tie_name)
	return (strongest_tie_rid,strongest_tie_name,steps)
    else:
        return ("","","")


def get_user_most_visited(rid):
	cl = connect()
	visited_count = {}
	visited_rest = cl.command("select distinct(name) as name, distinct(res_id) as res_id, distinct(cuisines) as cuisine from (select expand(both('eats_at')) from Person where @rid ="+str(rid)+")")
	(restaurant_visits,desc_visitcount,asc_visitcount) = count_visits(visited_rest)
	if desc_visitcount:
		return desc_visitcount
	else:
		return ""
#	(rest_name,rest_rid) = get_restaurant_name(desc_visitcount[0][0],1)

#ensure created_at is set to a time two weeks ago as well
def get_user_recent_visit(rid):
	cl = connect()
	recent_visits = cl.command("select @rid as rid,name from Restaurant where @rid in (select in from eats_at where out="+str(rid)+"  order by created_at_datetime desc)")
	if recent_visits:
		return recent_visits
	else:
		return ""

def check_existing_feedback(rest_rid,userid):
	cl  = connect()
	chk_feedback = cl.command("select * from dislikes where in="+str(rest_rid)+ " and out="+str(userid))
	if chk_feedback:
		return 0
	else:
		return 1
	
def get_rest_for_feedback(recent_visit,most_visited,user_id):
	i = 0
	j = 0
	while (recent_visit[i]):
		rest_rid = recent_visit[i].rid
		rest_name = recent_visit[i].name
		i=i+1
		if (check_existing_feedback(rest_rid,user_id)):
			return rest_name
		else:
			continue
	while (most_visited[j]):
		(rname,rest_rid) = get_restaurant_name(most_visited[j][0],1)
		j=j+1
		if (check_existing_feedback(rest_rid,user_id)):
			return rest_name
		else:
			continue
	
	return ""

def gen_feedback_card(userid):
#	(rid_recent,rname_recent) = get_recent_visit(userid)
#	(rid_frequent,rname_frequent) = get_most_visited(userid)
	recent_visit = get_user_recent_visit(userid)
	most_visited = get_user_most_visited(userid)
	if recent_visit and most_visited:
		rname = get_rest_for_feedback(recent_visit,most_visited,userid)
		print rname
		if rname:
			msg =  "Did you like the food at "+str(rname)+"?"
			cmd_str = 'create vertex Card set display_type="feedback",comment_list=[],like_list=[],user_response="",created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",text="'+msg+'"'
#			print cmd_str
			insert_card(cmd_str,userid)
		else:
			return #No feedback card to send
	else:
		return

def compare_monthly_activity(user_visits,friend_visits,name,userid):
	msg = '<table><p>Restaurant visit activity</p><tr><td></td><td>You</td><td>'+str(name)+'</td></tr><tr><td>Week1</td><td>'+str(user_visits[0])+'</td><td>'+str(friend_visits[0])+'</td></tr><tr><td>Week2</td><td>'+str(user_visits[1])+'</td><td>'+str(friend_visits[1])+'</td></tr><tr><td>Week3</td><td>'+str(user_visits[2])+'</td><td>'+str(friend_visits[2])+'</td></tr><tr><td>Week4</td><td>'+str(user_visits[3])+'</td><td>'+str(friend_visits[3])+'</td></tr></table>'
			#msg = ''+get_restaurant_name(dsorted_all_restaurant_visits[i][0])+'\tVisits:'+ str(dsorted_all_restaurant_visits[i][1])
#	print msg
	cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",text="'+msg+'"'
#	print cmd_str
#	insert_card(cmd_str,userid)

def insert_image(rid):
	tags = ["healthy","italian"]
	msg="2 out of 6 of the CS PhD students have eaten healthy over the past week"
#			 random_num = randint(1,23)
#			 filename = '/Local/Users/dev/NetworkLabs/topgenerator/data/img/food/'+str(random_num)+'.jpg'
	ret_val = begin_localimg(msg.replace("1 times","once"),"namedfriend_overlay_cuisine_monthly.jpg")
	if ret_val == 1:
		recid_img = create_binary_data("/Local/Users/dev/NetworkLabs/namedfriend_overlay_cuisine_monthly.jpg")
		cmd_str = 'create vertex Card set display_type="info",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",image="'+recid_img+'"'
		card_rid = insert_card(cmd_str,rid,1)
		id_rec = cl.command('create edge has_uploaded_image from '+str(card_rid)+' to '+str(recid_img))
		print id_rec[0].rid

def create_profile_page_cards(userid):
	
	creation_date=datetime.datetime.today()
	msg1 = "This week, you have walked a total of <b>2705 steps</b>"
	msg2 = "This week, you have eaten at <b>1 healthy restaurant</b>"
	msg3 = ""
	cmd_str1 = 'create vertex Card set display_type="profile_info",sub_display_type="message",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg1+'"'
	cmd_str2 = 'create vertex Card set display_type="profile_info",sub_display_type="message",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg2+'"'
	cmd_str3 = 'create vertex Card set display_type="profile_info",sub_display_type="graphic",net_walk_avg="2360",you_walk_avg="2567",net_eat="4",you_eat="2",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg1+'"'

	insert_card(cmd_str1,userid)
	insert_card(cmd_str2,userid)
	insert_card(cmd_str3,userid)


def count_steps_walked(all_stats):
	steps_walked = 0
	flag = 0
	for person_stats in all_stats:
		print person_stats
		if len(person_stats)>1:
			flag=1
		for stats in person_stats:
			print stats
			steps_walked+=stats.steps
	if flag==1:
		return steps_walked
	else:
		return -1

def user_stats_queries(userid):
	cl = connect()
	epoch_week = 1429548439
	last_epoch_week = 1428248439
	cmd_last_week = 'select name, res_id as res_id, steps_walked as steps from (select expand(in) from eats_at where created_at > "'+str(last_epoch_week)+'" and created_at < "'+str(epoch_week)+'" and out="'+str(userid)+'"and steps_walked > 0)'
	cmd_this_week = 'select name, res_id as res_id, steps_walked as steps from (select expand(in) from eats_at where created_at > "'+str(epoch_week)+'" and out="'+str(userid)+'"and steps_walked > 0)'

	visits_last_week = cl.command(cmd_last_week)
	visits_this_week = cl.command(cmd_this_week)
	return (visits_last_week,visits_this_week)

def network_stats_profile_page(user_steps_lw,user_steps_tw,user_visits_lw,user_visits_tw):
	res1 = cl.command("select * from Person")
	total_people = len(res1)
	steps_last_week = 0
	steps_this_week = 0
	all_visits_last_week = []
	all_visits_this_week = []

	#query stats of all users
	for i in range(total_people):
		userid = str(res1[i].rid)
		(visits_last_week,visits_this_week) = user_stats_queries(userid)
		all_visits_last_week.append(visits_last_week)
		all_visits_this_week.append(visits_this_week)

	#aggregate stats for all users
	(visit_last_week,asc_visits_lw,desc_visits_lw) = count_restaurants_visited(all_visits_last_week)
	(visit_this_week,asc_visits,desc_visits) = count_restaurants_visited(all_visits_this_week)
	steps_last_week = count_steps_walked(all_visits_last_week)
	steps_this_week = count_steps_walked(all_visits_this_week)

	# Compute averages
	if steps_last_week>0:
		avg_steps_this_week = (steps_this_week-user_steps_tw)/total_people
	if steps_this_week>0:
		avg_steps_last_week = (steps_last_week-user_steps_lw)/total_people
	if visit_this_week>0:
		avg_healthy_visits_this_week = (visit_this_week-user_visits_tw)/total_people
	if visit_last_week>0:
		avg_healthy_visits_last_week = (visit_last_week-user_visits_lw)/total_people
	if avg_steps_this_week>=0 and avg_steps_last_week>=0 and avg_healthy_visits_this_week>=0 and avg_healthy_visits_last_week>=0:
		return (avg_steps_this_week,avg_steps_last_week,avg_healthy_visits_this_week,avg_healthy_visits_last_week)
	else:
		return (-1,-1,-1,-1)

def profile_msgs(userid):
	(user_visit_lw_res,user_visits_tw_res) = user_stats_queries(userid)

	(visit_lw,asc_visits_lw,desc_visits_lw) = count_restaurants_visited([user_visit_lw_res])
        (visit_tw,asc_visits_tw,desc_visits_tw) = count_restaurants_visited([user_visits_tw_res])
        user_steps_lw = count_steps_walked([user_visit_lw_res])
        user_steps_tw = count_steps_walked([user_visits_tw_res])
	
	(nw_steps_tw,nw_steps_lw,nw_visits_tw,nw_visits_lw) = network_stats_profile_page(visit_lw,visit_tw,user_steps_lw,user_steps_tw)
	if visit_lw>=0 and visit_tw>=0 and user_steps_lw>=0 and user_steps_tw>=0 and nw_steps_tw>=0 and nw_steps_lw>=0 and nw_visits_tw>=0 and nw_visits_lw>=0:
		creation_date=datetime.datetime.today()
		msg1 = "This week, you have walked a total of <b>"+str(user_steps_tw)+"steps"
		msg2 = "This week, you have eaten at <b>"+str(visit_tw)+" healthy restaurants</b>"
		cmd_str1 = 'create vertex Card set display_type="profile_info",sub_display_type="message",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg1+'"'
		cmd_str2 = 'create vertex Card set display_type="profile_info",sub_display_type="message",comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",html_content="'+msg2+'"'
		cmd_str3 = 'create vertex Card set display_type="profile_info",sub_display_type="graphic",net_walk_avg='+str(nw_steps_lw)+',you_walk_avg='+str(user_steps_lw)+',net_eat='+str(nw_visits_lw)+',you_eat='+str(visit_lw)+',comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))

		insert_card(cmd_str1,userid)
		insert_card(cmd_str2,userid)
		insert_card(cmd_str3,userid)


if __name__ == '__main__':
	cl = connect()
	print "Connected"
	peopleid = cl.command("select @rid from Person where first_name='Pranav'")
	noofpeople = len(peopleid)
	creation_date=datetime.datetime.today()
	#print "Restaurants visited by network- positive messages"
       # rest_visited_by_network("#12:108",1,"")
	#print "Restaurants visited by network- negative messages"
      #  rest_visited_by_network("#12:108",-1,"")
	#print "Generating feedback card"
#	gen_feedback_card("#12:2520")
#	insert_image(peopleid[0].rid)
#	profile_msgs(peopleid[0].rid)
	create_profile_page_cards(peopleid[0].rid)
#	print "Inserted"
#	profile_msgs(peopleid[0].rid)
	
	for i in range(len(peopleid)):
		
		print "\n\n\n\n"+str(peopleid[i].rid)
		print "Restaurants visited by network- positive messages"
		rest_visited_by_network(peopleid[i].rid,1,"")
		print "Restaurants visited by network- negative messages"
		rest_visited_by_network(peopleid[i].rid,-1,"")

		
		print "Restaurants visited by friends- positive messages"
		rest_visited_by_friends(peopleid[i].rid,1,"")
		print "Restaurants visited by friends- negative messages"
		rest_visited_by_friends(peopleid[i].rid,-1,"")
		print "This is the most influential positive message"
		print most_influential_msg_pos
		print "This is the most influential negative message"
		print most_influential_msg_neg
		print "Finding strongest tie based on restaurants visited"
		(friend_rid,friend_name,steps) = get_strongest_tie_rest_visit(peopleid[i].rid)
		if friend_rid!="" and friend_name!="": 
			gen_stats_named_friend(peopleid[i].rid,friend_rid,friend_name,steps,1)
	  	 	gen_stats_named_friend(peopleid[i].rid,friend_rid,friend_name,steps,-1)

			visit_list_user = get_monthly_stats(peopleid[i].rid)
			visit_list_friend = get_monthly_stats(friend_rid)
			compare_monthly_activity(visit_list_user,visit_list_friend,friend_name,peopleid[i].rid)
	        print "Finding strongest tie based on comment and likes"

        	print "Finding strongest tie based on cuisine preferred"
    		
		print "Generating statistics for people with similar preferences"
		rest_visited_similar_pref(peopleid[i].rid,"")

		gen_feedback_card(peopleid[i].rid)
#		create_profile_page_cards(peopleid[i].rid)
	

#cmd_str = 'create vertex Card set comment_count=0,comment_list=[],like_count=0,like_list=[],people_involved=[],created_at="'+str(int(creation_date.strftime('%s'))*1000)+'",created_at_datetime="'+str(creation_date.strftime('%Y-%m-%d'))+'",text="'+mesg+'"'
		#print cmd_str
	#	insert_card(cmd_str,peopleid[i].rid)
	
		#Graph listing the healthiest restauruants in Champaign-Urbana	
