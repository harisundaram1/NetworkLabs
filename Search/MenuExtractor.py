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
