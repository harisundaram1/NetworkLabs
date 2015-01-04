import math
def rad(x):
        return x * math.pi / 180

def getDistance(srclatlong, dstlatlong):
        R = 6378137L
        dLat = rad(dstlatlong[0] - srclatlong[0])
        dLong = rad(dstlatlong[1] - srclatlong[1])
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(srclatlong[0])) * math.cos(rad(dstlatlong[0])) * math.sin(dLong / 2) * math.sin(dLong / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d

def displace(latitude,longitude,disp):
	R = 111111
	disp_lat = float(disp) / R
	disp_long = float(disp) / ( R * math.cos( latitude * float(math.pi / 180) ) )
	lat_off = latitude + disp_lat 
	long_off = longitude + disp_long 
	return (lat_off, longitude),(latitude, long_off)

if __name__ == "__main__":
	a = (40.080772, -88.19044)
	b,c = displace(40.080772, -88.19044,200)
	print b
	print c
	print getDistance(a, b)
	print getDistance(a, c)
	print getDistance((40.080772,-88.30315), (40.0816720009,-88.3019737397))
