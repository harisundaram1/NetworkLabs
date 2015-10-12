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
from collections import defaultdict

# Function - to read the json dumps
def readJsonDumps():
    grid_points = json.load(open('grid_points'))
    grid_cells = json.load(open('grid_cells'))
    return (grid_points, grid_cells)

# Function - to hash restaurants to their respective cells - reduces the calls required.
def hashToRestaurant(rest_data, grid):
    print "\nHashing Restaurant to Grid cell"
    grid_hash = defaultdict(list)
    for rest in rest_data:
        geo = rest_data[rest][1]
        for item in grid:
            cell = []
            temp = item.replace('(','').replace(')','').replace(' ','').split(',')
            for i in [0,2,4,6]:
                cell.append(temp[i:i+2])
            min_point = cell[0]
            max_point = cell[2]
            if float(min_point[0]) <= geo[0] and geo[0] <= float(max_point[0]):
                if float(min_point[1]) <= geo[1] and geo[1] <= float(max_point[1]):
                    grid_hash[item].append((rest,geo))
    print "\nFinished hashing"
    return grid_hash


if __name__ == "__main__":
    
    #Read the saved json dumps
    grid_points, grid_cells = readJsonDumps()
    grid_hash = hashToRestaurant(grid_points, grid_cells)
    
    #Save the grid hash
    json.dump(grid_hash, open('grid_hash','w'))
