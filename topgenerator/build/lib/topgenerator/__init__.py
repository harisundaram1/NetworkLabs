import pyorient
import orientmodel as om
from .gen import *

if __name__ == "__main__":
	cl = om.connect('NetworkLabs','root','root','localhost')
	# print cl