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

import topgenerator as tp
import datetime
import cProfile, pstats, StringIO

tp.clear_network()
###### tp.create_restaurants()
try:
	tp.create_binary_data()
except Exception, e:
	print "Image saving timed out"
else:
	print 'Image saving completed'
tp.generate_friends_network(100,10,0.1,"small")
cl = tp.connect()
# Create profile Image
cmd_str = 'select * from Person'
users = cl.command(cmd_str)
tp.create_has_profile_image_edge(users)
cmd_str = 'select * from Person where @rid not in '+str(tp.get_exception_user_rid()).replace("'","")
print cmd_str	
users = cl.command(cmd_str)
print len(users)
start_date = datetime.datetime(2015, 1, 1)
end_date = datetime.datetime.today()
delta = datetime.timedelta(days=1)
# pr = cProfile.Profile()
# pr.enable()
while start_date <= end_date:
	print ''
	print '=======creating activities for '+start_date.strftime('%Y-%m-%d')+'========'
	tp.create_activity_cards(users,start_date)
	print '=======creating comments/likes for '+start_date.strftime('%Y-%m-%d')+'========'
	tp.create_comment_likes(users,start_date)
	start_date += delta
# tp.get_cosine_similarity_for_users(users)
# # pr.disable()
# # s = StringIO.StringIO()
# # sortby = 'cumulative'
# # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# # ps.print_stats()
# # print s.getvalue()
