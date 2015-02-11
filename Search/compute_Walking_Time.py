import json
import csv
import urllib2
import datetime
import time
from collections import defaultdict

# Function - to calculate the walking duration between two given points
def getDuration(srcAddress, dstAddress):
	# Setting the Google Places API key
	AUTH_KEY = 'AIzaSyACzP9Vt7RxrLFqwsG4SkVGRIiSJC1kEWo'

	# Transform the source and destination address into Google API format
	#srcAddress = srcAddress.replace(', ',' ').replace(',',' ').replace(' ','+') 
	#dstAddress = dstAddress.replace(', ',' ').replace(',',' ').replace(' ','+')

	# Compose a URL to query a predefined location with a radius of 5000 m
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + srcAddress + "&destinations=" + dstAddress + "&mode=walking"

	# Send the GET request to the Place details service (using aove url)
	response = urllib2.urlopen(url)

	# Processing the response
	json_raw = response.read()
	json_data = json.loads(json_raw)

	# Traverse the json to extract the time in seconds
	if json_data['status'] == 'OK':
		rows = json_data['rows'][0]
		elements = rows["elements"][0]
		duration = elements["duration"]
		time = duration["value"]
		# Return the time in seconds	
		return time
	else:
		# Couldnt find the distance - default to a large value
		print "Error",json_data['status']
        exit()
        return 9999

# Function - to read the json dumps
def readJsonDumps():
    grid_points = json.load(open('grid_points'))
    grid_cells = json.load(open('grid_cells'))
    grid_hash = json.load(open('grid_hash'))
    return (grid_points, grid_cells, grid_hash)

# Function - compute the walking times
def computeWalkingTime(rest_data, grid, hashgrid):
    print "\nBeginning to compute the walking time"
    index = 49
    cells = grid.keys()[0:2400]         # 3127 Batch 1 : 2500 (0-2499), Batch 2: 627 (2500-3126)
    rest_ids = rest_data.keys()         # 192
    rest_groups = hashgrid.keys()[index]    # 97  Batch 1 : 37 (0-36), Batch 2: 30 (37-66), Batch 3: 30 (67-96)

    rest = hashgrid[rest_groups][0]

    res_id = rest[0]
    src = str(rest[1][0])+ ',' + str(rest[1][1])
    data = []
    counter = 1

    print "\nStarting calls to Google API"
    for item in cells:
        # Convert cell center to string
        dst = str(grid[item][0])+ ',' + str(grid[item][1])

        # Calling function that determines the walking distance using Google API
        walking_time = getDuration(src,dst)
        
        # Each row in data - Res_id, Cell Center, Walking time.
        data.append([res_id,dst,walking_time])

        if len(hashgrid[rest_groups]) > 1:
            for i in range(1, len(hashgrid[rest_groups])):
                rest = hashgrid[rest_groups][i]
                res_id = rest[0]
                src = str(rest[1][0])+ ',' + str(rest[1][1])
                data.append([res_id,dst,walking_time])
        
        counter += 1
        
        if counter % 100 == 0:
            print "\nFinished 100 requests sleeping for 15 seconds. Counter at", counter
            time.sleep(15)

    # save data in csv with current timestamp as filename
    filename =  str(index) + "-" +str(datetime.datetime.now()) + ".csv" 
    writeData(filename, data)

# Function - to save the data as a csv
def writeData(filename, results):
    print "\nSaving data as csv"

    csvfile = open(filename, "wb")

    data_writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    data_writer.writerow(['res_id','cell_center','walk_time'])

    for item in results:
        data_writer.writerow(item)
    csvfile.close()

    print "\nFinished extracting the data and storing in file"

if __name__ == "__main__":
    
    #Read the saved json dumps
    grid_points, grid_cells, grid_hash = readJsonDumps()

    #Compute walking time
    computeWalkingTime(grid_points, grid_cells, grid_hash)


