from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from xml.etree.ElementTree import Element, SubElement, Comment
from ElementTree_pretty import prettify
import ast

app = Flask(__name__)

@app.route('/submit_config', methods=['POST'])
def submit_config():
	print "Processing the submitted configurations"

	top = Element('top')
	comment = Comment('Config File')
	top.append(comment)

	# Checking for null values
	if request.form['db_name']:
		db_name = request.form['db_name']
		child = SubElement(top, 'Database_Name')
		child.text = db_name

	if request.form.get('person'):
		person = request.form['person']
		child = SubElement(top, 'Person')
		child.text = person

	if request.form.get('base_entity'):
		base_entity = request.form['base_entity']
		child = SubElement(top, 'Base_Entity')
		child.text = base_entity

	if request.form.get('card'):
		card = request.form['card']
		child = SubElement(top, 'Child')
		child.text = card

	if request.form['num_users']:
		num_users = request.form['Num_of_users']
		child = SubElement(top, 'child')
		child.text = child

	if request.form['network_type'] != "no":
		network_type = request.form['Network_Topology']
		child = SubElement(top, 'child')
		child.text = network_type

	if request.form['num_friends']:
		num_friends = request.form['Num_of_friends']
		child = SubElement(top, 'child')
		child.text = num_friends

	recalibrate = request.form['recalibrate']
	child = SubElement(top, 'Recalibrate_Network')
	child.text = recalibrate

	if request.form['single_user']:
		single_user = request.form['single_user']
		child = SubElement(top, 'Single_User')
		child.text = single_user

	if request.form.get('clear_network'):
		clear_network = request.form['clear_network']
		child = SubElement(top, 'Clear_Network')
		child.text = clear_network

	output_xml = prettify(top)

	outfile = open('config.xml',"w")
	outfile.write(output_xml)
	outfile.close()

	# Call Method to create Database along with the class names

	# Call method to configure the number of users, network topology, number of friends and recalibrate if necessary

	# Call method to add single user

	# Call method to add custo friends from input file

	# Call method to clear the network

	return "Posted"
    
if __name__ == '__main__':
	app.debug = True
	app.run()