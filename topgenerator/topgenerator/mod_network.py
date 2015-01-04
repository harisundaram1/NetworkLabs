import snap, csv, random, re, math, datetime, os, base64, urllib,  urllib2, json
from .connect_db import *
from pyorient.utils import *
import numpy as np
import scipy.spatial.distance


# This is the file where we manipulate the files
def to_snap(nodes=[],edge_type=''):
	# INPUT: Node List, edge type 