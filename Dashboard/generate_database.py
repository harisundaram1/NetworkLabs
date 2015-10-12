Copyright (c) 2015 Crowd Dynamics Labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


import snap, csv, random, re, math, datetime, os, base64, urllib,  urllib2, json, db
from pyorient.utils import *
import numpy as np
# import scipy.spatial.distance
# import topgenerator as tp
import xml.etree.ElementTree as ET
# Read the configuration file.
# Create the relevant classes which are selected

def read_config_file(file_path):
	tree = ET.parse(file_path)
	root = tree.getroot()
	print root.tag
	print root.attrib
	config_map = {}
	for child in root:
		config_map[child.tag.lower()] = True if child.text  == 'on' else child.text
		print child.tag
		print child.text
	print config_map
	return config_map

def create_database(configs):
	db_name = configs['database_name']
	create_person = True if 'person' in configs else False
	create_base_entity = True if 'base_entity' in configs else False
	create_card = True if 'card' in configs else False

	cl = connect()

	#create database 
	cl.db_create(db_name, pyorient.DB_TYPE_GRAPH, pyorient.STORAGE_TYPE_PLOCAL)
	cl.db_open(db_name, "admin", "admin")

	# Create classes
	if create_person:
		cl.command('Create class Person extends V')
	if create_base_entity:
		cl.command('Create class BaseEntity extends V')
	if create_card:
		cl.command('Create class Card extends V')

def connect():
	client = pyorient.OrientDB("localhost", 2424)
	session_id = client.connect( "root", "root" )
	return client

if __name__ == '__main__':
	configs = read_config_file('config_data/network_config.xml')
	if 'database_name' in configs:
		create_database(configs)
