import sys
import os.path

stop_words = ['beef','pork','lamb','ham','shrimp','creamy','fried','fry','bacon','sausage','seafood','ribs','salami','crab','b.b.q.','bbq','rib','ribs','steak','pepperoni','b.b.q','sausage','wings']
stop_words = set(stop_words)

def getScore(filename):
    filename = "backup/" + filename
    if os.path.isfile(filename):
        infile = open(filename,"r")
        count = 0.0
        total = 0.0
        for line in infile:
            total += 1.0
            flag = 0
            items = line.rstrip().split('###')
	    items = ' '.join(items).split()
	    #print items
            for word in items:
                if word.lower() in stop_words:
                    flag = 1
                    break
            if flag == 0:
                count += 1.0
        infile.close()
	if total == 0.0:
		score = 0.0
        	print "\nScore for: " + filename + " --> " + str(score) 
		return score
        score = count / total
        print "\nScore for: " + filename + " --> " + str(score) 
	return score
	
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
    print "\nScoring\n"
    #rest_url = parseFile(sys.argv[1])
    #for rest in rest_url:
    getScore(sys.argv[1])
    print "\nFinished Scoring\n"
