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
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=0.2, random_state=0)
    print "Finished splitting the data,evaluating now"
    clf = svm.SVC(kernel='linear', C=1).fit(X_train, y_train)
    print "Finished fitting the data and cross validating"
    print clf.score(X_test, y_test)


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
