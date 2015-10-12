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

import re
import csv
from collections import defaultdict
from sklearn import cross_validation
from sklearn import svm

def read_csv(filename):
    data_path = '/home/moontails/work/'
    temp = []
    infile = open(data_path + filename,'r')
    csvfile = csv.reader(infile)
    headers = csvfile.next()
    for row in csvfile:
        data = {headers[i]:row[i] for i in xrange(len(headers))}
        temp.append(data)
    return temp


def cross_validate(data):
    '''Perform five fold cross validation'''

    X = [ [i] for i in data.keys() ]
    Y = data.values()
    Errors = []
    for i in range(5):
        print "Round:",i
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=0.2, random_state=0)

        print "Finished splitting the data,evaluating now"
        classifier = svm.SVR(kernel='linear')
        classifier.fit(X_train, y_train)
        #print "Finished fitting the data and cross validating"
        #print clf.score(X_test, y_test)

        print "Making the predictions and calculating the results"
        error = []

        for j in range(len(X_test)):
            error.append( classifier.predict(X_test[j]) - y_test[j] )

        Errors.append(float(sum(error))/len(error))

    print "Average Error is ",Errors


if __name__ == "__main__":
    non_decimal = re.compile(r'[^\d.]+')
    distance = read_csv('Total.csv')
    distance_hash = defaultdict()
    print distance[0]

    for item in distance:
        k = int( item['distance'] )
        v = float( non_decimal.sub('',item['walk_time']) )
        distance_hash[k] = v

    cross_validate(distance_hash)
