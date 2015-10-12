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
