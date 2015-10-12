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


import os
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from werkzeug import secure_filename
from xml.etree.ElementTree import Element, SubElement, Comment
from ElementTree_pretty import prettify
import ast


UPLOAD_FOLDER = '~/NetworkLabs/Dashboard/config_data/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def hello():
    return render_template('dashboard.html')



@app.route('/network_config', methods=['POST'])
def network_config():
	print "Processing the submitted configurations for Network"
	# flag to print debug statements, enable only during development or during debugging.
	debug = 0

	# a top element for the config file - to hold a brief description
	top = Element('top')
	comment = Comment('Config File for Network')
	top.append(comment)

	# Checking for null values
	#   - if not null then extract value and add it to xml tree

	if request.form['db_name']:
		db_name = request.form['db_name']

		if debug: print db_name

		child = SubElement(top, 'Database_Name')
		child.text = db_name

	if request.form.get('person'):
		person = request.form['person']

		if debug: print person

		child = SubElement(top, 'Person')
		child.text = person

	if request.form.get('base_entity'):
		base_entity = request.form['base_entity']

		if debug: print base_entity

		child = SubElement(top, 'Base_Entity')
		child.text = base_entity

	if request.form.get('card'):
		card = request.form['card']

		if debug: print card

		child = SubElement(top, 'Card')
		child.text = card

	if request.form['num_users']:
		num_users = request.form['num_users']
		if debug: print num_users
		child = SubElement(top, 'Num_of_users')
		child.text = child

	if request.form['network_type'] != "no":
		network_type = request.form['network_type']

		if debug: print network_type

		child = SubElement(top, 'Network_Topology')
		child.text = network_type

	if request.form['num_friends']:
		num_friends = request.form['num_friends']

		if debug:  print num_friends

		child = SubElement(top, 'Num_of_friends')
		child.text = num_friends

	recalibrate = request.form['recalibrate']
	if debug:  print recalibrate
	child = SubElement(top, 'Recalibrate_Network')
	child.text = recalibrate

	if request.form['single_user']:
		single_user = request.form['single_user']

		if debug: print single_user

		child = SubElement(top, 'Single_User')
		child.text = single_user

	if request.form.get('clear_network'):
		clear_network = request.form['clear_network']

		if debug: print clear_network

		child = SubElement(top, 'Clear_Network')
		child.text = clear_network

	if request.method == 'POST':
		infile = request.files['custom_friends']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

	# Prettify the xml before writing to file
	output_xml = prettify(top)
	print "Saving the config file for Network"
	# save in config_data file.
	# make sure to change the path to store the config file here
	outfile = open('config_data/network_config.xml',"w")
	outfile.write(output_xml)
	outfile.close()

	return "Success! Network configurations saved"

@app.route('/info_display_config', methods=['POST'])
def info_display_config():
	print "Processing the submitted configurations for Information Display"
	# flag to print debug statements, enable only during development or during debugging.
	debug = 0

	# a top element for the config file - to hold a brief description
	top = Element('top')
	comment = Comment('Config File for Information Display')
	top.append(comment)

	if request.form['threshold_positive']:
		threshold_positive = request.form['threshold_positive']

		if debug: print threshold_positive

		child = SubElement(top, 'Threshold_Positive')
		child.text = threshold_positive

	if request.form['threshold_negative']:
		threshold_negative = request.form['threshold_negative']

		if debug: print threshold_negative

		child = SubElement(top, 'Threshold_Positive')
		child.text = threshold_negative

	if request.form['threshold_per_day']:
		threshold_per_day = request.form['threshold_per_day']

		if debug: print threshold_per_day

		child = SubElement(top, 'Threshold_Per_Day')
		child.text = threshold_per_day

	if request.form['threshold_time']:
		threshold_time = request.form['threshold_time']

		if debug: print threshold_time

		child = SubElement(top, 'Threshold_Time')
		child.text = threshold_time

	if request.form['threshold_hierarchy']:
		threshold_hierarchy = request.form['threshold_hierarchy']

		if debug: print threshold_hierarchy

		child = SubElement(top, 'Threshold_Hierarchy')
		child.text = threshold_hierarchy

	if request.form['flickr_api']:
		flickr_api = request.form['flickr_api']

		if debug: print threshold_hierarchy

		child = SubElement(top, 'Flickr_API_Key')
		child.text = flickr_api

	if request.method == 'POST':
		infile = request.files['positive_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['negative_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['neutral_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['weekly_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['monthly_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['all_time_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['spatial_stats_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['network_stats_messages']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['messages_with_images']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

		infile = request.files['messages_with_tables']

		if debug: print infile

		if infile and allowed_file(infile.filename):
			filename = secure_filename(infile.filename)
			infile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			child = SubElement(top, 'File_for_custom_friends')
			child.text = os.path.join(app.config['UPLOAD_FOLDER'], filename)

	# Prettify the xml before writing to file
	output_xml = prettify(top)
	print "Saving the config file for Information Display"
	# save in config_data file.
	# make sure to change the path to store the config data here
	outfile = open('config_data/info_display_config.xml',"w")
	outfile.write(output_xml)
	outfile.close()

	return "Success! Information Display configurations saved"

if __name__ == '__main__':
	app.debug = True
	app.run(port=5002)
