from flask import Flask
from flask import request
from flask import jsonify
import searchapi
import ast
import walk_calculations

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World!"

@app.route("/search", methods=['POST'])
def search():
	print "Search called with data:" + request.data
	search_param = ast.literal_eval(request.data)
	print search_param['userid']
	print search_param['query']

	ret = searchapi.search_res(search_param['userid'], search_param['query'], search_param['latitude'], search_param['longitude'])
	ret = jsonify(result=ret)
	print ret
	print("end of function")
	return ret 

@app.route("/checkin_search", methods=['POST'])
def checkin_search():
	print "checkin_search called with data:" + request.data 
	checkin_search_param = ast.literal_eval(request.data)
	print checkin_search_param['longitude']
	print checkin_search_param['longitude']


	ret = searchapi.checkin_search(checkin_search_param['latitude'], checkin_search_param['longitude'])
	ret = jsonify(result=ret)
	print ret
	print("end of function")
	return ret 

@app.route("/steps_walked", methods=['POST'])
def calculate_steps_walked():
	print "steps_walked called with data:" + request.data 
	steps_param = ast.literal_eval(request.data)
	print steps_param['cardId']
	
	ret = walk_calculations.steps_walked(steps_param['cardId'])
	ret = jsonify(result=ret)
	print ret
	print("end of function")
	return ret 


if __name__ == "__main__":
	app.debug = True
	app.run(port=5000)
