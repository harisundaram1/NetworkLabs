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
