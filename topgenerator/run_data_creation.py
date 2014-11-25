import topgenerator as tp
import datetime
import cProfile, pstats, StringIO

tp.clear_network()
# tp.create_restaurants()
try:
	tp.create_binary_data()
except Exception, e:
	print "Image saving timed out"
else:
	print 'Image saving completed'
tp.create_users_network(1000,30,0.1,"small")
# cl = tp.connect()
# cmd_str = 'select * from Person where @rid not in '+str(tp.get_exception_user_rid()).replace("'","")
# print cmd_str	
# users = cl.command(cmd_str)
# print len(users)
# start_date = datetime.datetime(2014, 10, 27)
# end_date = datetime.datetime.today()
# delta = datetime.timedelta(days=1)
# # pr = cProfile.Profile()
# # pr.enable()
# while start_date <= end_date:
# 	print ''
# 	print '=======creating activities for '+start_date.strftime('%Y-%m-%d')+'========'
# 	tp.create_activity_cards(users,start_date)
# 	start_date += delta
# tp.get_cosine_similarity_for_users(users)
# # # pr.disable()
# # # s = StringIO.StringIO()
# # # sortby = 'cumulative'
# # # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# # # ps.print_stats()
# # # print s.getvalue()