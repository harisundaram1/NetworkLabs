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

import json
import csv
import pyorient
import math
import os
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn import svm
from sklearn import cross_validation

def connect():
    '''Function to connect to the database'''
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect( "root", "rootlabs" )
    client.db_open( "NetworkLabs", "admin", "admin")
    return client

def rad(x):
    '''Function to convert degree into radians'''
    return x * math.pi / 180

def get_distance(srclat, srclong, dstlat, dstlong):
    '''Function to calculate the Haversian distance between two geo locations'''
    #print "In the get distance function"
    R = 6378137L
    dLat = rad(dstlat - srclat)
    dLong = rad(dstlong - srclong)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(srclat)) * math.cos(rad(dstlat)) * math.sin(dLong / 2) * math.sin(dLong / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d

def read_json_dumps():
    '''Function to read the json dumps and build the hashes'''
    #Replace the path accordingly
    path = '/Users/moontails/NetworkLabs/Search/'
    grid_points = json.load(open(path + 'grid_points'))
    grid_cells = json.load(open(path + 'grid_cells'))
    grid_hash = json.load(open(path + 'grid_hash'))
    return (grid_points, grid_cells, grid_hash)

def read_csv():
    data_path = '/Users/moontails/NetworkLabs/distance_data/'
    files = os.listdir(data_path)
    temp = []
    for filename in files:
        infile = open(data_path + filename,'r')
        csvfile = csv.reader(infile)
        headers = csvfile.next()
        for row in csvfile:
            data = {headers[i]:row[i] for i in xrange(len(headers))}
            temp.append(data)
    return temp

def dump_csv(results, filename):
    print "\nSaving data as csv"

    csvfile = open(filename, "wb")

    data_writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    data_writer.writerow(['distance','walk_time'])

    for item in results:
        temp = [item,results[item]]
        data_writer.writerow(temp)
    csvfile.close()

    print "\nFinished extracting the data and storing in file"

def rest_dict(grid_hash):
    '''Function to create and return a restaurant dict of the form result[restaurant] = [lat,long]'''
    result = defaultdict()
    for cell in grid_hash:
        temp = grid_hash[cell]
        for item in temp:
            result[item[0]] = item[1]
    return result

def predict_using_svm(train_data, test_data):
    '''Fitting a classifier using SVM Regression and predicting the values
            using linear kernel and perform five fold cross validation
    '''
    print "\nPredicting using SVM"
    X = [ [i] for i in train_data.keys() ]
    Y = train_data.values()

    classifier = svm.SVR(kernel='linear')
    classifier.fit(X,Y)
    print "Starting the predictions"
    #predict for the test data
    for distance in test_data:
        test_data[distance] = classifier.predict([distance])

    #Dump the values
    print "\nDumping the training and test data"
    dump_csv(train_data, "Train.csv")
    dump_csv(test_data, "Test.csv")
    #scores = cross_validation.cross_val_score(classifier, X, Y, cv=5)

    #print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

def drawGridPoints(X, Y):
    '''Function - to plot the points forming the grid'''
    plt.plot(X,Y)
    plt.show()

def load_distances_to_hash(grid_cells):
    # Return the test and total distance hash
    t_hash = defaultdict()
    d_hash = defaultdict()
    for cell_center in grid_cells:
        dst_geo = grid_cells[cell_center]
        dstlat,dstlong = float(dst_geo[0]),float(dst_geo[1])

        for res_id in grid_points:
            src_geo = grid_points[res_id][1]
            srclat,srclong = float(src_geo[0]),float(src_geo[1])
            distance = int(get_distance(srclat, srclong, dstlat, dstlong))
            d_hash[distance] = 0
            t_hash[distance] = 0

    return t_hash,d_hash

def compute_training_data(grid_points,distance_hash,train_data,test_data):
    for item in data_list:
        res_id    = item['res_id']
        #points[item['cell_center']] = 1
        src_geo   = item['cell_center'].split(',')
        walk_time = item['walk_time']
        #print walk_time
        dst_geo   = grid_points[res_id][1]

        srclat,srclong = float(src_geo[0]),float(src_geo[1])
        dstlat,dstlong = float(dst_geo[0]),float(dst_geo[1])

        distance = int(get_distance(srclat, srclong, dstlat, dstlong))

        train_data[distance] = walk_time
        distance_hash[distance] = walk_time
        if distance in test_data:
            del test_data[distance]

if __name__ == "__main__":
    #Read the saved json dumps
    grid_points, grid_cells, grid_hash = read_json_dumps()

    #Read the csv files data - this is the csv produced by the compute walking time script
    data_list = read_csv()

    #To store the distance and walkign time computed in training
    train_data = defaultdict()

    #To store the distance and walkign time to be computed using training and To hold all possible distances
    test_data,distance_hash = load_distances_to_hash(grid_cells)

    print "\nNumber of unique distance values:", len(distance_hash)

    #Populate the training data and remove them from test data
    compute_training_data(grid_points,distance_hash,train_data,test_data)

    print "\nNumber of walking time values computed:", len(train_data)
    print "\nNumber of unique distance values: (Sanity Check)", len(distance_hash)
    print "\nNumber of walking time values to be computed:", len(test_data)

    # Predict using SVM
    predict_using_svm(train_data, test_data)

    for distance in test_data:
        distance_hash[distance] = test_data[distance]

    #five_fold_validation(distance_hash)
    # Visualizing the inputs
    #drawGridPoints(train_data.keys(),train_data.values())

    # Saving the Data
    print "\nDumping the full data"
    dump_csv(distance_hash, "Total.txt")
