import sys
import os
import pyorient

# list of stop words
stop_words = ['beef','pork','lamb','ham','shrimp','bacon','sausage','seafood','ribs','salami','crab','rib','steak','pepperoni','wings', 'chicen','duck','octopus','chorizo','sashimi','sushi','turkey','brisket','squid','salmon','tuna','turtle','eel','calamari','tonkatsu','crab','meat','meatball','fish','pig','fillet']

# converting to set for faster checking
stop_words = set(stop_words)

def connect():
        '''Function to connect to the database'''
        client = pyorient.OrientDB("localhost", 2424)
        session_id = client.connect( "root", "rootlabs" )
        client.db_open( "NetworkLabs", "admin", "admin")
        return client

def getScore(filename):
        # Constuct the path name
        filename = "backup/" + filename

        # check if the menu exists
        if os.path.isfile(filename):
                #open the menu for reading
                infile = open(filename,"r")

                # initialize the counts
                count = 0.0
                total = 0.0

                # for each menu item check if it is healthy or not
                for line in infile:
                        total += 1.0

                        # flag to set on detecting unhealthy menu item
                        flag = 0

                        # split the menu item using the delimiter '###'
                        items = line.rstrip().split('###')
                        items = ' '.join(items).split()

                        #print items

                        # loop over the menu items and increment count
                        for word in items:
                                if word.lower() in stop_words:
                                        # not healthy so skip incrementing count by setting flag
                                        flag = 1
                                        break

                                # else update count if flag is not set
                                if flag == 0:
                                        count += 1.0

		# close the file
                infile.close()

                # if file empty then score is 0.0
                if total == 0.0:
                        score = 0.0
                        print "\nScore for: " + filename + " --> " + str(score)
                        return score
                score = count
                print "\nScore for: " + filename + " --> " + str(score)

                # return the score
                return score

def compute_veg_options():
	'''Function to read each menu in the directory, call getScore and update db'''
	
	# obtain a client
	cl = connect()
	
	# obtain all the menus
	files = os.listdir("menus/")

	for filename in files:
		# compute the score
		score = getScore(filename)

		# construct the query base
		sql_query = "UPDATE Restaurant SET veg_options=%s WHERE res_id LIKE " % (score)+ "\'%" + filename + "%\'" 

		# run query and update the db
		cl.command(sql_query)
	
if __name__ == "__main__":
	print "Processing each file"

	compute_veg_options()

	print "Finished updating the db"
