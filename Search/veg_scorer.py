import sys
import os
import pyorient

stop_words = ['beef','pork','lamb','ham','shrimp','bacon','sausage','seafood','ribs','salami','crab','rib','steak','pepperoni','wings', 'chicen','duck','octopus','chorizo','sashimi','sushi','turkey','brisket','squid','salmon','tuna','turtle','eel','calamari','tonkatsu']
stop_words = set(stop_words)

def connect():
        '''Function to connect to the database'''
        client = pyorient.OrientDB("localhost", 2424)
        session_id = client.connect( "root", "rootlabs" )
        client.db_open( "NetworkLabs", "admin", "admin")
        return client

def getScore(filename):
    filename = "menus/" + filename
    if os.path.isfile(filename):
        infile = open(filename,"r")
        count = 0.0
        total = 0.0
        for line in infile:
            total += 1.0
            flag = 0
            items = line.rstrip().split('###')
	    items = ' '.join(items).split()
	    #print items
            for word in items:
                if word.lower() in stop_words:
                    flag = 1
                    break
            if flag == 0:
                count += 1.0
        infile.close()
	if total == 0.0:
		score = 0.0
        	print "\nScore for: " + filename + " --> " + str(score) 
		return score
        score = count 
        print "\nScore for: " + filename + " --> " + str(score) 
	return score

def compute_veg_options():
	'''Function to read each menu in the directory, call getScore and update db'''
	
	# obtain a client
	cl = connect()
	
	# obtain all the menus
	files = os.listdir("menus/")

	for filename in files:
		# construct the query base
		score = getScore(filename)
		sql_query = "UPDATE Restaurant SET veg_options=%s WHERE res_id LIKE " % (score)+ "\'%" + filename + "%\'" 
		cl.command(sql_query)
	
if __name__ == "__main__":
	print "Processing each file"

	compute_veg_options()

	print "Finished updating the db"
