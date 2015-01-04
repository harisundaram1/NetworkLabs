import json
import math
from collections import defaultdict
import urllib2
import connect_db as db 
import matplotlib.pyplot as plt

# Function - to convert degrees to radians
def rad(x):
        return x * math.pi / 180

# Function to get the distance between source and destination
def getDistance(srclatlong, dstlatlong):
        R = 6378137L
        dLat = rad(dstlatlong[0] - srclatlong[0])
        dLong = rad(dstlatlong[1] - srclatlong[1])
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(srclatlong[0])) * math.cos(rad(dstlatlong[0])) * math.sin(dLong / 2) * math.sin(dLong / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d

# Function to offset the given (latitude, longitude) by the provided displacement
def displace(latitude,longitude,disp):
        L = 111111
        disp_lat = float(disp) / L
        disp_long = float(disp) / ( L * math.cos( rad(latitude) ) )
        lat_off = latitude + disp_lat
        long_off = longitude + disp_long
        return (lat_off, longitude),(latitude, long_off)

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
		print "Error"
		return 9999

# Function - to obtain all the grid points for constructing the grid
def extractGridPoints():
	print "\nAccessing the database to retrieve the restaurant information"

	# Connect to the database and get all the restaurant data
	client = db.connect()
	sql_query = "SELECT FROM Restaurant"
	result = client.command(sql_query)
	
	# Extract the points that form the grid
	grid_points = defaultdict(list)
	for restaurant in result:
		# Convert Address for Google API readiness
		# Ex - 201+North+Goodwin+Avenue+Urbana+IL+61801
		address = restaurant.address.replace(', ',' ').replace(',',' ').replace(' ','+')
		# Store the lat long as a tuple
		lat_long = (restaurant.latitude, restaurant.longitude)
		
		# Insert into a dictionary of grid points
		grid_points[restaurant.res_id] = [address,lat_long]

	# Return a dictionary of Restaurant and Co-ordinate points
	print "\nFinished processing and extracting the coordinates"
	return grid_points

# Function - to construct the grid from the four corners
def createGrid(corners, offset):
	print "\nConstructing the grid from the four corners"
	# get the x co-ordinates
	x = [ item[0] for item in corners ] 	
	# get the y co-ordinates
	y = [ item[1] for item in corners ]

	# get the 4 points
	xmin = min(x)
	xmax = max(x)
	ymin = min(y)
	ymax = max(y)
	
	# compute the offset co-ordinates
	x = []
	y = []
	points = defaultdict(list)

	temp,count =  ymin,0
	L = 111111.0
	disp = offset / L

	while temp <= ymax:
		x.append(ymin + disp*count)
		temp += disp
		count += 1	

	for lat in x:
		disp = offset / ( L * math.cos(rad(lat)) )
		temp,count = xmin,0
		while temp<=xmax:
			lon = xmin + disp*count
			temp += disp
			count += 1
			y.append(lon)
			points[lat].append((lat, lon))

	print len(x), len(points), len(y)
	cell_corners = [ (i,j) for i in y for j in x ]
	
	grid_cells = defaultdict(tuple)
	
	dispx = offset / ( 2 * L )
	for i in range(len(x)-1):
		dispy = offset / (2 * L * math.cos(rad(x[i])))
		for j in range(len(points[x[i]])-1):
			#print points[x[i]][j],points[x[i]][j+1],points[x[i+1]][j+1],points[x[i+1]][j]
			#print points[x[i]][j][0] + dispx, points[x[i]][j][1] + dispy
			#exit()
			grid_key = (points[x[i]][j],points[x[i]][j+1],points[x[i+1]][j+1],points[x[i+1]][j])
			grid_cells[str(grid_key)] = (points[x[i]][j][0] + dispx, points[x[i]][j][1] + dispy)
	print "Total number of cells in the grid -",len(grid_cells)
	#drawGridPoints([i[1] for i in cell_corners],[i[0] for i in cell_corners],"New.png")
	# Return the grid cells
	print "\nFinished creating the grid, returning the cells"
	return grid_cells

# Function - to plot the points forming the grid
def drawGridPoints(lat, lon, filename="Grid.png"):
	print "\nProcessing the coordinates"
	fig = plt.figure()
	grid = fig.add_subplot(111)

	# X Co-ordinate points
	x_points = lon
	# Y Co-ordinate points
	y_points = lat

	# Setting the axis
	p = grid.plot(x_points, y_points, 'b')

	# Setting Labels
	grid.set_xlabel('Longitude')
	grid.set_ylabel('Latitude')
	grid.set_title('Geo-Plot of Latitude & Longitude')

	#fig.show() # To show the drawn grid of points
	plt.grid() # To show a Grid
	fig.savefig(filename) # To save the grid in png format.
	print "\nFinished saving the image to disk"

# Function - to compute the four corners of the grid
def findCorners(points):
	print "\nFinding the four corners of the Grid"
	# Get the Co-ordinates
	grid_points = [ x[1] for x in points.values() ]
	
	# Get the Latitudes
	lat = [ x[0] for x in grid_points ]

	# Get the Longitudes
	lon = [ x[1] for x in grid_points ]

	# Draw the Grid
 	#drawGridPoints(lat,lon)	

	#Get the Four Bounds of the GRID - (xmin,ymin) (xmin,ymax) (xmax,ymin) (xmax,ymax)
	ymin = min(lat)
	ymax = max(lat)
	xmin = min(lon)
	xmax = max(lon)
	
	corners = [ (xmin,ymin),(xmin,ymax), (xmax,ymin), (xmax,ymax) ]
	
	# Return the four corners
	print "\nFinished computing the four corners of the Grid"
	return corners

# Function - to hash restaurants to their respective cells
def hashToRestaurant(rest_data, grid):
	print "\nHashing Restaurant to Grid cell"	
	grid_hash = defaultdict(list)
	for rest in rest_data:
		geo = rest_data[rest][1]
		for cell in grid:
			min = cell[0]
			max = cell[2]
			if min[0] <= geo[0] and geo[0] <= max[0]:
				if min[1] <= geo[1] and geo[1] <= max[1]:
					grid_hash[cell].append((rest,geo))
	print "\nFinished hashing"
	return grid_hash

# Function to save to database:
def saveToDB(rest_data, grid, hash):
	client = db.connect()
	for cell in grid:
		src = grid[cell]
		sql_query = "insert into Grid CONTENT "
		for rest in rest_data:
			dst = rest_data[rest][1]
					

# Function to save as a csv
def saveToCSV(rest_data, grid, hash):
	client = db.connect()
	#for cell
	

if __name__ == "__main__":
	# Extract the Grid
	grid_points = extractGridPoints()
	
	# Get the Grid Corners
	grid_corners = findCorners(grid_points)

	# Create the Grid
	offset = 200
	grid_cells = createGrid(grid_corners, offset)

	grid_hash = hashToRestaurant(grid_points, grid_cells)
	
	print "\nDumping grid_points, grid_cells and grid_hash"
	json.dump(grid_points, open('grid_points','w'))
	json.dump(grid_cells, open('grid_cells','w'))
	json.dump(grid_hash, open('grid_hash','w'))
	print "\nFinished dumping the data using json"
	#saveToDB(grid_points,grid_cells,grid_hash)
	#saveToCSV(grid_points,grid_cells,grid_hash)

