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

import sys
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup

def getMenu(page_url):
    print page_url
  #  try:
    page = urlopen(page_url)
    html = page.read()
    print "\nPage read successful"
    soup = BeautifulSoup(html)
    dishes = []
    filename = "menus/" + page_url.split('/')[-2]
    print filename
    outfile = open(filename,"w")
    for dish in soup.find_all('li'):
        for name in dish.find('div'):
            menu_item = name.string.encode('ascii', 'ignore').strip(), dish['title'].encode('ascii', 'ignore')
            outfile.write(menu_item[0] + " - " + menu_item[1])
            outfile.write("\n")
    outfile.close()
    print "Finished writing menu to file" + page_url
#    except:
 #       print "\nNo Menu exists for: " + page_url
	
def parseFile(filename):
    infile = open(filename,"r")
    base_url = "https://www.noshfolio.com"
    links = []
    for line in infile:
        rest_link = line.strip().strip('"')
        links.append(base_url + rest_link + "/dishes")
    infile.close()
    return links

if __name__ == "__main__":
	# Pass the link
    rest_url = parseFile(sys.argv[1])
    for rest in rest_url:
        getMenu(rest)
    print "Finished collecting the menus\n"
